import os
import json
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
import boto3
import re

load_model = AutoModelForSequenceClassification.from_pretrained("model/")
load_tokenizer = AutoTokenizer.from_pretrained("model/")

def clean_and_split_text(text):
    # Remove links
    text = re.sub(r"<http[s]?://[^>]+>", "", text)
    # Remove user mentions
    text = re.sub(r"<@[^>]+>", "", text)
    # Remove emojis
    text = re.sub(r":\S+:", "", text)
    # Remove symbols and special characters
    text = re.sub(r"[^\w\s.]", " ", text)
    # Split into sentences using periods and new lines
    sentences = re.split(r"[.!?]+\s*|\n", text)
    # Remove empty lines
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

def have_high_score_sick_label(objects):
    return any(obj["label"] == "SICK" and obj["score"] > 0.9 for obj in objects)

def publish_to_sns(message):
    client = boto3.client("sns")
    response = client.publish (
        TargetArn = os.environ["SNS_TOPIC_ARN"],
        Message = json.dumps({"slack_message": message})
    )
    print("SNS response: " + json.dumps(response, indent=2))

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    sick_leave_detector = pipeline(
        "text-classification",
        model=load_model,
        tokenizer=load_tokenizer
    )

    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])["slack_message"]
        predictions = sick_leave_detector(clean_and_split_text(message["text"]))
        print("Predictions: " + json.dumps(predictions, indent=2))
        if have_high_score_sick_label(predictions):
            publish_to_sns(message)

    return True
