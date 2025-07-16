# AwsAiProd - Bedrock LLM Production Pipe

Complete AWS LLM infra with fine-tuning, evaluation, and deployment using Bedrock, Step Functions, DynamoDB, Lambda etc.


## Quick Start

1. **Set GitHub Secrets**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`

2. **Deploy**
   ```bash
   git push origin main
   # GitHub Actions triggers Step Functions pipeline
   ```

3. **Test Chat**
   ```bash
   # Get API URL from GitHub Actions output
   export API_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod/chat
   
   cd test_chat
   docker build -t chat .
   docker run -it -e API_URL=$API_URL -v ~/.aws:/root/.aws chat
   ```

## Project Structure

```
AwsAiProd/
├── app/                        # Complete application
│   ├── lambda_function.py      # Chat API handler
│   ├── template.yml            # SAM template for infrastructure
│   ├── state_machine.json      # Step Functions orchestration
│   ├── data/
│   │   ├── train.jsonl         # Training examples
│   │   └── eval.jsonl          # Evaluation examples
│   └── functions/
│       ├── prepare_data.py     # Data validation Lambda
│       └── evaluate_model.py   # Model evaluation Lambda
├── test_chat/
│   ├── Dockerfile              # Container for test client
│   └── test_chat.py           # Interactive chat client
├── .github/
│   └── workflows/
│       └── cicd.yml           # GitHub Actions deployment
│   └── policies/
│       ├── lambda-trust-policy.json
│       ├── lambda-execution-policy.json
│       ├── bedrock-trust-policy.json
│       ├── bedrock-finetuning-policy.json
│       ├── stepfunctions-trust-policy.json
│       └── stepfunctions-policy.json
└── .gitignore

```

## Detailed Setup

### Prerequisites

1. AWS account with Bedrock access enabled
2. IAM user with permissions for:
   - Lambda, API Gateway, DynamoDB
   - S3, Step Functions, IAM roles
   - Bedrock model access

### Manual Deployment Steps

If not using GitHub Actions:

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://bedrock-training-data-${AWS_ACCOUNT_ID}
   ```

2. **Deploy Lambda and DynamoDB**
   ```bash
   cd src
   sam deploy --guided
   ```

3. **Upload Training Data**
   ```bash
   aws s3 cp fine_tuning/data/training.jsonl s3://bedrock-training-data-${AWS_ACCOUNT_ID}/
   aws s3 cp fine_tuning/data/validation.jsonl s3://bedrock-training-data-${AWS_ACCOUNT_ID}/
   ```

4. **Create IAM Roles**
   
   BedrockFineTuningRole trust policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": {"Service": "bedrock.amazonaws.com"},
       "Action": "sts:AssumeRole"
     }]
   }
   ```
   
   StepFunctionsBedrockRole trust policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": {"Service": "states.amazonaws.com"},
       "Action": "sts:AssumeRole"
     }]
   }
   ```

5. **Deploy Step Functions**
   ```bash
   aws stepfunctions create-state-machine \
     --name BedrockFineTuning \
     --definition file://fine_tuning/state_machine.json \
     --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/StepFunctionsBedrockRole
   ```

### Running Fine-Tuning and Evaluation

Start the workflow:
```bash
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:${AWS_ACCOUNT_ID}:stateMachine:BedrockFineTuning \
  --input '{"accountId": "YOUR_ACCOUNT_ID"}'
```

The workflow automatically:
1. Deploys infrastructure (Lambda, API Gateway, DynamoDB)
2. Fine-tunes model with training data
3. Evaluates model performance
4. Updates Lambda with fine-tuned model if evaluation passes

Monitor in AWS Console → Step Functions → BedrockApplicationPipeline

### Data Preparation

Validate training data:
```bash
python fine_tuning/scripts/prepare_data.py fine_tuning/data/training.jsonl
```

Test a model:
```bash
python fine_tuning/scripts/evaluate_model.py amazon.titan-text-lite-v1
```

### Troubleshooting

- **API Gateway timeout**: Increase Lambda timeout in template.yaml
- **DynamoDB errors**: Check table exists and IAM permissions
- **Bedrock access denied**: Enable model access in Bedrock console
- **Step Functions fail**: Check CloudWatch logs for detailed errors

## Architecture

1. **API Layer**: Lambda + API Gateway for chat interface
2. **Storage**: DynamoDB for conversation history
3. **Orchestration**: Step Functions for fine-tuning workflow
4. **Model Service**: Bedrock for LLM inference and customization