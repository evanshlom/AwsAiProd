import json
import boto3

def lambda_handler(event, context):
    """
    Lambda function to validate JSONL format for Bedrock fine-tuning
    Called by Step Functions before training
    """
    s3 = boto3.client('s3')
    
    bucket = event['bucket']
    key = event['key']
    
    # Download file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    
    valid_lines = 0
    errors = []
    
    for i, line in enumerate(content.strip().split('\n'), 1):
        try:
            data = json.loads(line)
            if 'prompt' not in data or 'completion' not in data:
                errors.append(f"Line {i}: Missing required fields")
            else:
                valid_lines += 1
        except json.JSONDecodeError as e:
            errors.append(f"Line {i}: Invalid JSON - {e}")
    
    if errors:
        return {
            'statusCode': 400,
            'valid': False,
            'validLines': valid_lines,
            'errors': errors[:10]  # Return first 10 errors
        }
    
    return {
        'statusCode': 200,
        'valid': True,
        'validLines': valid_lines,
        'message': f"All {valid_lines} lines validated successfully"
    }