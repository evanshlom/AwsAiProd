import boto3
import json
import time
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Deploy or update CloudFormation stack
    """
    cf = boto3.client('cloudformation')
    account_id = event['accountId']
    action = event.get('action', 'deploy')
    model_id = event.get('modelId', 'anthropic.claude-3-haiku-20240307')
    
    stack_name = 'llm-chat-stack'
    template_url = f'https://s3.amazonaws.com/llm-training-data-{account_id}/template.yml'
    
    # Check if stack exists and its status
    try:
        stacks = cf.describe_stacks(StackName=stack_name)
        stack_status = stacks['Stacks'][0]['StackStatus']
        
        if stack_status in ['ROLLBACK_COMPLETE', 'ROLLBACK_FAILED']:
            # Delete the failed stack
            cf.delete_stack(StackName=stack_name)
            # Wait for deletion
            waiter = cf.get_waiter('stack_delete_complete')
            waiter.wait(StackName=stack_name)
    except ClientError as e:
        if 'does not exist' not in str(e):
            raise
    
    parameters = [{
        'ParameterKey': 'ModelId',
        'ParameterValue': model_id
    }]
    
    try:
        if action == 'deploy':
            # Try to create stack
            try:
                cf.create_stack(
                    StackName=stack_name,
                    TemplateURL=template_url,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
                )
                # Wait for creation to start
                time.sleep(5)
            except cf.exceptions.AlreadyExistsException:
                # Stack exists, update it
                cf.update_stack(
                    StackName=stack_name,
                    TemplateURL=template_url,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
                )
        else:
            # Update with new model
            cf.update_stack(
                StackName=stack_name,
                UsePreviousTemplate=True,
                Parameters=parameters,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
            )
        
        # Get stack outputs
        time.sleep(10)
        response = cf.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0].get('Outputs', [])
        
        return {
            'statusCode': 200,
            'stackName': stack_name,
            'outputs': {o['OutputKey']: o['OutputValue'] for o in outputs}
        }
        
    except Exception as e:
        # If stack is in bad state, delete and recreate
        if 'ROLLBACK_COMPLETE' in str(e):
            cf.delete_stack(StackName=stack_name)
            time.sleep(60)
            return lambda_handler(event, context)  # Retry
        raise e