import json
import logging
import os
import boto3
import pymysql
from botocore.exceptions import ClientError
from db_conn import connect_to_db


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
        logging.error(f"Response: {response}")
        return True
    except client.exceptions.UserNotFoundException:
        return False
    except ClientError as e:
        logging.error(f"ERROR: {e}")
        raise e


def email_exists_in_cognito(email):
    client = boto3.client('cognito-idp', region_name='us-east-1')
    user_pool_id = os.getenv('USER_POOL_ID')

    try:
        response = client.list_users(
            UserPoolId=user_pool_id,
            Filter=f"email=\"{email}\""
        )
        logging.error(f"Response: {response}")
        if response['Users']:
            return True
        else:
            return False
    except ClientError as e:
        logging.error(f"ERROR: {e}")
        raise e


def insert_user_db(uid, name, lastname, age, gender):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (uid, name, lastname, status, age, gender) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (uid, name, lastname, 'activo', age, gender))
            connection.commit()
            return True
    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()

