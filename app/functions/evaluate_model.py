import boto3
import json

bedrock = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    """
    Lambda function to evaluate model performance
    Called by Step Functions after fine-tuning
    """
    model_id = event['modelId']
    test_prompts = event.get('testPrompts', [
        "What events happen at Allegiant Stadium?",
        "Tell me about Vegas pool parties",
        "Plan a budget weekend trip"
    ])
    
    results = []
    errors = 0
    
    for prompt in test_prompts:
        try:
            # Test with Titan model format
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 200,
                        "temperature": 0.7
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            completion = response_body['results'][0]['outputText']
            
            # Check if response mentions key Vegas/Allegiant terms
            keywords = ['allegiant', 'vegas', 'flight', 'stadium', 'strip']
            relevance_score = sum(1 for k in keywords if k.lower() in completion.lower())
            
            results.append({
                "prompt": prompt,
                "response": completion[:200],
                "relevant": relevance_score >= 2,
                "status": "success"
            })
            
        except Exception as e:
            errors += 1
            results.append({
                "prompt": prompt,
                "response": None,
                "relevant": False,
                "status": "error",
                "error": str(e)
            })
    
    # Pass if at least 80% of prompts succeeded and were relevant
    successful_relevant = sum(1 for r in results if r['status'] == 'success' and r['relevant'])
    pass_threshold = len(test_prompts) * 0.8
    
    return {
        'passed': successful_relevant >= pass_threshold,
        'score': f"{successful_relevant}/{len(test_prompts)}",
        'results': results
    }