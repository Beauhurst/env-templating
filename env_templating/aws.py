import json

import boto3


def get_aws_secret(session: boto3.session.Session, secret_name: str) -> dict:
    client = session.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
