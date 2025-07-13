import boto3
import json

def lambda_handler(event, context):
    """
    Check status of Bedrock fine-tuning job
    """
    bedrock = boto3.client('bedrock')
    job_arn = event['jobArn']
    
    # Extract job name from ARN
    job_name = job_arn.split('/')[-1]
    
    try:
        response = bedrock.get_model_customization_job(
            jobIdentifier=job_name
        )
        
        status = response['status']
        
        result = {
            'status': status,
            'jobArn': job_arn
        }
        
        if status == 'Completed':
            result['customModelArn'] = response['outputModelArn']
        elif status == 'Failed':
            result['failureMessage'] = response.get('failureMessage', 'Unknown error')
            
    except Exception as e:
        # If we can't find the job, it might still be starting
        result = {
            'status': 'InProgress',
            'jobArn': job_arn,
            'error': str(e)
        }
    
    return result