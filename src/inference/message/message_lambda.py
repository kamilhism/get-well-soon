import os
import json
import boto3

def slack_verify(request_body):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({ "challenge": request_body.get("challenge")  })
    }

def publish_to_sns(request_body):
    client = boto3.client("sns")
    response = client.publish (
        TargetArn = os.environ["SNS_TOPIC_ARN"],
        Message = json.dumps({"slack_message": request_body["event"]})
    )
    print("SNS response: " + json.dumps(response, indent=2))

def handler(event, context):
    request_body = json.loads(event["body"])

    if request_body.get("challenge"):
        return slack_verify(request_body)

    if request_body.get("event"):
        publish_to_sns(request_body)

    return True
