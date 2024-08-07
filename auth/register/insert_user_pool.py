import json
import logging
import os
import boto3
from botocore.exceptions import ClientError


def insert_user_pool(email, username, password, role):
    try:
        client = boto3.client('cognito-idp', region_name='us-east-1')
        user_pool_id = os.getenv('USER_POOL_ID')

        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'false'},
            ],
            TemporaryPassword=password
        )

        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=role
        )

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "User created successfully, verification email sent."})
        }
    except ClientError as e:
        logging.error(f"ERROR: {e}")
        raise e
    except Exception as e:
        logging.error(f"ERROR: {e}")
        raise e


def user_exists_in_cognito(username):
    client = boto3.client('cognito-idp', region_name='us-east-1')
    user_pool_id = os.getenv('USER_POOL_ID')

    try:
        response = client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        return True
    except client.exceptions.UserNotFoundException:
        return False
    except ClientError as e:
        logging.error(f"ERROR: {e}")
        raise e
