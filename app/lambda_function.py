import boto3
import json
import os

bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ConversationHistory')

def lambda_handler(event, context):
    try:
        # Get model ID from environment variable (updated by Step Functions)
        model_id = os.environ.get('MODEL_ID', 'anthropic.claude-3-haiku-20240307')
        
        body = json.loads(event['body'])
        prompt = body.get('prompt', '')
        history = body.get('history', [])
        session_id = body.get('session_id')
        
        # Build messages array with history
        messages = []
        for msg in history[-10:]:  # Last 10 messages
            messages.append(msg)
        messages.append({"role": "user", "content": prompt})
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "messages": messages,
                "max_tokens": 1000,
                "anthropic_version": "bedrock-2023-05-31"
            })
        )
        
        response_body = json.loads(response['body'].read())
        assistant_message = response_body['content'][0]['text']
        
        # Save to DynamoDB if session_id provided
        if session_id:
            import time
            timestamp = int(time.time() * 1000)
            
            # Save user message
            table.put_item(Item={
                'session_id': session_id,
                'timestamp': timestamp,
                'message': {"role": "user", "content": prompt}
            })
            
            # Save assistant response
            table.put_item(Item={
                'session_id': session_id,
                'timestamp': timestamp + 1,
                'message': {"role": "assistant", "content": assistant_message}
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': assistant_message
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }