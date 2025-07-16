# IAM Policies

This directory contains all IAM policies used in the deployment pipeline.

## Trust Policies (for AssumeRole)
- `lambda-trust-policy.json` - Allows Lambda service to assume roles
- `bedrock-trust-policy.json` - Allows Bedrock service to assume roles  
- `stepfunctions-trust-policy.json` - Allows Step Functions to assume roles

## Permission Policies
- `lambda-execution-policy.json` - Full permissions for Lambda functions (CloudFormation, Bedrock, S3, etc.)
- `bedrock-finetuning-policy.json` - S3 access for Bedrock fine-tuning jobs
- `stepfunctions-policy.json` - Allows Step Functions to invoke Lambda functions

## Usage
These are referenced in the cicd.yml workflow using:
```bash
--policy-document file://.github/policies/<policy-name>.json
```

## Adding New Policies
1. Create a new JSON file following AWS IAM policy format
2. Reference it in cicd.yml using the file:// prefix
3. Document its purpose here