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
    training_job_name = f"llm-tune-{timestamp}"
    
    response = bedrock.create_model_customization_job(
        jobName=training_job_name,
        customModelName=f"allegiant-vegas-model-{timestamp}",
        baseModelIdentifier="amazon.titan-text-lite-v1",
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