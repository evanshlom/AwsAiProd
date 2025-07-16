FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install requests boto3

# Copy test script
COPY test_chat.py .

# Copy .env file
COPY .env ./

# Set environment variables
ENV AWS_DEFAULT_REGION=us-east-1

# Run the test chat
CMD ["python", "-u", "test_chat.py"]