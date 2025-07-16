import requests
import boto3
import time
import uuid
import json
import os

# Load .env file
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# Get API URL from environment or use placeholder
API_URL = os.environ.get('API_URL', 'https://your-api-gateway-url.amazonaws.com/Prod/chat')

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('ConversationHistory')

# Generate session ID
session_id = str(uuid.uuid4())
print(f"Chat Session: {session_id}")
print(f"API URL: {API_URL}")
print("Type 'quit' to exit\n")

def get_conversation_history(session_id):
    """Retrieve conversation history from DynamoDB"""
    try:
        response = table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id}
        )
        return [item['message'] for item in response.get('Items', [])]
    except Exception as e:
        print(f"Warning: Could not retrieve history from DynamoDB: {e}")
        return []

while True:
    prompt = input("You: ")
    
    if prompt.lower() == 'quit':
        print("Goodbye!")
        break
    
    # Get conversation history
    history = get_conversation_history(session_id)
    
    # Prepare request
    request_data = {
        "prompt": prompt,
        "history": history[-10:],  # Last 10 messages
        "session_id": session_id
    }
    
    try:
        # Send request to API
        response = requests.post(
            API_URL,
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            assistant_response = data.get('response', 'No response received')
            print(f"\nClaude: {assistant_response}\n")
        else:
            print(f"\nError: {response.status_code} - {response.text}\n")
            
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to API: {e}\n")
    except Exception as e:
        print(f"\nUnexpected error: {e}\n")