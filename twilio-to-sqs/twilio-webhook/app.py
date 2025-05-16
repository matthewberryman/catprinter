import os
import json
import boto3
import urllib.parse
from botocore.exceptions import ClientError
from twilio.request_validator import RequestValidator

def get_twilio_auth_token():
    secrets_client = boto3.client('secretsmanager')
    secret_id = os.environ.get('TWILIO_SECRET_ID', 'twilio/webhook')
    try:
        secret_response = secrets_client.get_secret_value(SecretId=secret_id)
        secret_string = secret_response.get('SecretString', '{}')
        secret_dict = json.loads(secret_string)
        return secret_dict.get('TWILIO_AUTH_TOKEN', '')
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return ''

sqs = boto3.client('sqs')
queue_url = os.environ['QUEUE_URL']
twilio_auth_token = get_twilio_auth_token()

validator = RequestValidator(twilio_auth_token)

def lambda_handler(event, context):
    # Extract the form-urlencoded body
    body = event.get('body', '')
    headers = event.get('headers', {})
    twilio_signature = headers.get('X-Twilio-Signature') or headers.get('x-twilio-signature')

    # Reconstruct the full URL that Twilio called, including stage and path
    protocol = headers.get('X-Forwarded-Proto', 'https')
    # Use requestContext.path to include the API Gateway stage in the URL
    url = f"{protocol}://{headers.get('Host')}{event['requestContext']['path']}"

    # Decode parameters from body
    params = urllib.parse.parse_qs(body)
    params = {k: v[0] for k, v in params.items()}  # Flatten values

    # Signature validation temporarily disabled
#    if not validator.validate(url, params, twilio_signature):
#        return {
#            'statusCode': 403,
#            'body': 'Forbidden: Invalid Twilio signature'
#        }

    # Extract fields
    sms_body = params.get('Body', '')
    from_number = params.get('From', '')
    to_number = params.get('To', '')

    # Send to SQS
    message = {
        'from': from_number,
        'to': to_number,
        'body': sms_body
    }

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    }