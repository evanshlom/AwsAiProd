import boto3
import json

def lambda_handler(event, context):
    """
    Create and start a Bedrock fine-tuning job
    """
    bedrock = boto3.client('bedrock')
    account_id = event['accountId']
    timestamp = event['timestamp']
    
    # Create fine-tuning job
    # Convert timestamp to valid format (remove colons and dots)
    clean_timestamp = timestamp.replace(':', '-').replace('.', '-').replace('T', '-').replace('Z', '')
    training_job_name = f"llm-tune-{clean_timestamp}"
    custom_model_name = f"allegiant-vegas-model-{clean_timestamp}"
    
    response = bedrock.create_model_customization_job(
        jobName=training_job_name,
        customModelName=custom_model_name,
        baseModelIdentifier="amazon.titan-text-g1-express",
        trainingDataConfig={
            "s3Uri": f"s3://llm-training-data-{account_id}/train.jsonl"
        },
        outputDataConfig={
            "s3Uri": f"s3://llm-training-data-{account_id}/output/"
        },
        hyperParameters={
            "epochCount": "3",
            "batchSize": "8", 
            "learningRate": "0.00001"
        },
        roleArn=f"arn:aws:iam::{account_id}:role/BedrockFineTuningRole"
    )
    
    return {
        'statusCode': 200,
        'jobArn': response['jobArn'],
        'modelArn': response.get('modelArn', 'pending')
    }