import json

import boto3


def get_aws_credentials(session: boto3.session.Session) -> tuple[str, str]:
    if session is None:
        session = boto3.Session()
    credentials = session.get_credentials()
    return credentials.access_key, credentials.secret_key


def get_aws_secret(session: boto3.session.Session, secret_name: str) -> dict:
    client = session.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
