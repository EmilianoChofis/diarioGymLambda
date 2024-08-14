import json
import logging
import os
import boto3
import jwt
from botocore.exceptions import ClientError
from db_conn import connect_to_db


def get_user_role(sub):
    try:
        client = boto3.client('cognito-idp', region_name='us-east-1')
        user_pool_id = os.getenv('USER_POOL_ID')
        response = client.admin_get_user(
            UserPoolId=user_pool_id,
            Filter=f"sub=\"{sub}\""
        )
        groups = response.get('UserAttributes', [])
        for attribute in groups:
            if attribute['Name'] == 'cognito:groups':
                return attribute['Value']
        return None
    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return None

def lambda_handler(event, __):
    try:
        headers = event.get('headers')
        if headers is None:
            return create_response(401, "No tienes permisos para realizar esta acción.")

        access_token = headers.get('Authorization')
        if not access_token or not access_token.startswith("Bearer "):
            return create_response(401, "No tienes permisos para realizar esta acción.")

        access_token = access_token.split(" ")[1]
        claims = jwt.decode(access_token, options={"verify_signature": False})

        connection = connect_to_db()
        if connection is None:
            return create_response(500, "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde.")

        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            users = cursor.fetchall()

            users_with_roles = []
            for user in users:
                uid = user['uid']
                role = get_user_role(uid)
                user['role'] = role
                users_with_roles.append(user)

            return create_response(200, "Lista de usuarios obtenidos", users_with_roles)

    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return create_response(400, f"Error en la conexión. {e}")
    except Exception as e:
        logging.error(f"ERROR: {e}")
        return create_response(500, f"Error de servidor. {e}")

def create_response(status_code, message, data=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps({
            "message": message,
            "data": data
        })
    }
    return response
