import os
import json
import boto3
import urllib3

dynamodb = boto3.client("dynamodb")

def put_reaction(message, token):
    http = urllib3.PoolManager()
    http.request("POST", "https://slack.com/api/reactions.add",
        body=json.dumps({
            "channel": message["channel"],
            "name": "four_leaf_clover",
            "timestamp": message["ts"]
        }),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

def get_token(message):
    team_id = message["team"]
    response = dynamodb.get_item(
        TableName=os.environ["DYNAMO_TABLE_NAME"],
        Key={"team_id": {"S": team_id}}
    )
    return response["Item"]["token"]["S"]

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])["slack_message"]
        put_reaction(message, get_token(message))

    return True
