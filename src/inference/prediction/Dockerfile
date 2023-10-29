FROM huggingface/transformers-pytorch-cpu

RUN pip install awslambdaric sentencepiece torch boto3

COPY prediction_lambda.py ./

ADD model ./model

ENTRYPOINT ["python3", "-m", "awslambdaric"]

CMD ["prediction_lambda.handler"]
