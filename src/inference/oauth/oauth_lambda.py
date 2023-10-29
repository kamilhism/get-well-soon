import os
import json
import boto3
import urllib3

def save_token(response):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["DYNAMO_TABLE_NAME"])
    table.put_item(
        Item={
            "team_id": response["team"]["id"],
            "token": response["access_token"]
        }
    )

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    http = urllib3.PoolManager()
    response = http.request_encode_body(
        "POST",
        "https://slack.com/api/oauth.v2.access",
        encode_multipart=False,
        fields={
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
            "code": event["queryStringParameters"]["code"]
        }
    )
    data = json.loads(response.data.decode("utf-8"))
    print("Data: " + json.dumps(data, indent=2))

    save_token(data)

    return {
        "statusCode": 200,
        "body": "Installed!",
        "headers": {
            "Content-Type": "text/html",
        }
    }
