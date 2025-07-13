import boto3
import json
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput, Processor
from sagemaker.estimator import Estimator
from sagemaker import get_execution_role
from sagemaker.workflow.parameters import ParameterString

def lambda_handler(event, context):
    """
    Create and start a SageMaker Pipeline for Bedrock fine-tuning
    """
    sagemaker = boto3.client('sagemaker')
    account_id = event['accountId']
    timestamp = event['timestamp']
    
    # Define pipeline parameters
    pipeline_name = f"bedrock-fine-tuning-{timestamp}"
    role = f"arn:aws:iam::{account_id}:role/SageMakerExecutionRole"
    
    # Create Bedrock fine-tuning job via SageMaker
    training_job_name = f"bedrock-tune-{timestamp}"
    
    # Start the training job directly (since SageMaker Pipelines doesn't have native Bedrock support yet)
    bedrock = boto3.client('bedrock')
    
    response = bedrock.create_model_customization_job(
        jobName=training_job_name,
        customModelName=f"allegiant-vegas-model-{timestamp}",
        baseModelIdentifier="amazon.titan-text-lite-v1",
        trainingDataConfig={
            "s3Uri": f"s3://llm-training-data-{account_id}/train.jsonl"
        },
        validationDataConfig={
            "s3Uri": f"s3://llm-training-data-{account_id}/eval.jsonl"  
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