import json

import boto3


def get_aws_secret(secret_name: str, aws_profile_name: str, aws_region_name: str) -> dict:
    """Retrieve a secret from AWS Secrets Manager"""
    session = boto3.Session(profile_name=aws_profile_name, region_name=aws_region_name)
    client = session.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
