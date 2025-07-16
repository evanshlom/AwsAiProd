import boto3
import json
import os

bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ConversationHistory')

def lambda_handler(event, context):
    try:
        # Get model ID from environment variable (updated by Step Functions)
        model_id = os.environ.get('MODEL_ID', 'amazon.titan-text-express-v1')
        
        body = json.loads(event['body'])
        prompt = body.get('prompt', '')
        history = body.get('history', [])
        session_id = body.get('session_id')
        
        # Build conversation text for Titan
        conversation_text = ""
        for msg in history[-10:]:  # Last 10 messages
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_text += f"{role}: {content}\n"
        conversation_text += f"user: {prompt}\nassistant:"
        
        # Call Bedrock with Titan format
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "inputText": conversation_text,
                "textGenerationConfig": {
                    "maxTokenCount": 512,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        assistant_message = response_body['results'][0]['outputText']
        
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