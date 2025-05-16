import boto3

import json

from catprinter.cmds import PRINT_WIDTH
from catprinter.txt import text_to_image

def fetch_and_print_from_sqs(queue_url, aws_region='ap-southeast-2', max_messages=1, wait_time=10):
    """
    Fetches messages from the given SQS queue, converts the message body to an image,
    and prints it using functions from txt.py.
    """
    sqs = boto3.client('sqs', region_name=aws_region)
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_time
    )
    messages = response.get('Messages', [])
    if messages:
        last_msg = messages[-1]
        print(last_msg)
        # Parse the JSON payload from the SQS 'Body' field
        raw_body = last_msg.get('Body', '')
        try:
            payload = json.loads(raw_body)
            text = f"From {payload.get('from')}: {payload.get('body')}"
            print(f"Parsed message: {text}")
        except json.JSONDecodeError:
            # Fallback to raw body if parsing fails
            text = raw_body

        # Delete only the last message after processing
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=last_msg['ReceiptHandle']
        )
        return text_to_image(text, PRINT_WIDTH)  # Adjust print_width as needed