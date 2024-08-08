import boto3
import os
import logging

from botocore.exceptions import ClientError


def get_secret():
    secret_name = os.getenv('SECRET_NAME')
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logging.error(f"Error getting secret value: {e}")
        raise e

    secret = get_secret_value_response['SecretString']
    return secret
