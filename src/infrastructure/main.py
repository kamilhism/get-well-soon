import os

from aws_cdk import (
    aws_lambda as _lambda,
    aws_efs as efs,
    aws_ec2 as ec2,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb
)
from aws_cdk import App, Stack, Duration
from constructs import Construct

from dotenv import load_dotenv

load_dotenv()

class GetWellStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.unprocessed_messages_sns = self._build_topic("unprocessed_messages")
        self.processed_messages_sns = self._build_topic("processed_messages")

        self.tokens_db = self._build_db()

        self._build_oauth_lambda_with_api_proxy(self.tokens_db)
        self._build_message_lambda_with_api_proxy(self.unprocessed_messages_sns)
        self._build_prediction_lambda(self.unprocessed_messages_sns, self.processed_messages_sns)
        self._build_reaction_lambda(self.processed_messages_sns, self.tokens_db)

    def _build_topic(self, name: str) -> sns.Topic:
        return sns.Topic(self, name, display_name=name)

    def _build_db(self) -> dynamodb.Table:
        return dynamodb.Table(
            self,
            "tokens",
            partition_key={"name": "team_id", "type": dynamodb.AttributeType.STRING},
        )

    def _build_oauth_lambda_with_api_proxy(self, tokens_db: dynamodb.Table):
        oauth_lambda = _lambda.Function(
            self,
            "oauth_lambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="oauth_lambda.handler",
            code=_lambda.Code.from_asset("../inference/oauth"),
            environment={
                "DYNAMO_TABLE_NAME": tokens_db.table_name,
                "CLIENT_ID": os.environ["CLIENT_ID"],
                "CLIENT_SECRET": os.environ["CLIENT_SECRET"]
            }
        )
        self._build_api_proxy_for_lambda("oauth_api", oauth_lambda)
        tokens_db.grant_read_write_data(oauth_lambda)

    def _build_message_lambda_with_api_proxy(self, unprocessed_messages_sns: sns.Topic):
        message_lambda = _lambda.Function(
            self,
            "message_lambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="message_lambda.handler",
            code=_lambda.Code.from_asset("../inference/message"),
            environment={
                "SNS_TOPIC_ARN": unprocessed_messages_sns.topic_arn
            }
        )
        unprocessed_messages_sns.grant_publish(message_lambda)
        self._build_api_proxy_for_lambda("message_api", message_lambda)

    def _build_api_proxy_for_lambda(self, name: str, lambda_func: _lambda.Function):
        api = apigateway.RestApi(
            self,
            name,
            default_cors_preflight_options={
                "allow_origins": apigateway.Cors.ALL_ORIGINS,
                "allow_methods": apigateway.Cors.ALL_METHODS,
                "allow_headers": ["*"],
            }
        )
        api_resource = api.root.add_resource("{proxy+}")
        api_proxy = api_resource.add_method(
            "ANY",
            apigateway.LambdaIntegration(lambda_func)
        )

    def _build_prediction_lambda(self, unprocessed_messages_sns: sns.Topic, processed_messages_sns: sns.Topic):
        prediction_lambda = _lambda.DockerImageFunction(
            self,
            "prediction_lambda",
            code=_lambda.DockerImageCode.from_image_asset("../inference/prediction",
                cmd=[
                    "prediction_lambda.handler"
                ]
            ),
            memory_size=8096,
            timeout=Duration.seconds(600),
            environment={
                "TRANSFORMERS_CACHE": "/mnt/hf_models_cache",
                "SNS_TOPIC_ARN": processed_messages_sns.topic_arn
            }
        )
        unprocessed_messages_sns.add_subscription(subs.LambdaSubscription(prediction_lambda))
        processed_messages_sns.grant_publish(prediction_lambda)

    def _build_reaction_lambda(self, processed_messages_sns: sns.Topic, tokens_db: dynamodb.Table):
        reaction_lambda = _lambda.Function(
            self,
            "reaction_lambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="reaction_lambda.handler",
            code=_lambda.Code.from_asset("../inference/reaction"),
            environment={
                "DYNAMO_TABLE_NAME": tokens_db.table_name
            }
        )
        processed_messages_sns.add_subscription(subs.LambdaSubscription(reaction_lambda))
        tokens_db.grant_read_write_data(reaction_lambda)

app = App()
GetWellStack(app, "GetWellStack")
app.synth()
