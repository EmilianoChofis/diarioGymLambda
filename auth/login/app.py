import json
import os
import logging
import boto3
from botocore.exceptions import ClientError

from queries import get_user


def get_user_id_by_username(username):
    client = boto3.client('cognito-idp', region_name='us-east-1')
    user_pool_id = os.getenv('USER_POOL_ID')

    try:
        response = client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        logging.error(f"Response: {response}")
        user_attributes = response['UserAttributes']

        # Buscar el atributo 'sub' en la lista de atributos
        uid = None
        for attribute in user_attributes:
            if attribute['Name'] == 'sub':
                uid = attribute['Value']
                break

        if uid:
            return uid
        else:
            raise ResourceNotFound("No se encontró el uuid del usuario.")
    except client.exceptions.UserNotFoundException:
        raise ResourceNotFound("No se encontró el usuario.")
    except client.exceptions.ClientError as e:
        logging.error(f"Error al buscar el usuario: {e}")
        raise e

class ResourceNotFound(Exception):
    """Raised when a resource is not found in the database."""
    pass

def lambda_handler(event, __):
    client = boto3.client('cognito-idp', region_name='us-east-1')
    client_id = os.getenv('CLIENT_ID')

    try:
        body_parameters = json.loads(event["body"])
        username = body_parameters.get('username')
        password = body_parameters.get('password')

        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Obtén los grupos del usuario
        user_groups = client.admin_list_groups_for_user(
            Username=username,
            UserPoolId=os.getenv('POOL_ID')  # Reemplaza con tu User Pool ID
        )

        # Determina el rol basado en el grupo
        role = None
        if user_groups['Groups']:
            role = user_groups['Groups'][0]['GroupName']  # Asumiendo un usuario pertenece a un solo grupo

        uid = get_user_id_by_username(username)

        user = get_user(uid)

        if not user:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({"error_message": "Usuario no encontrado."})
            }

        if user['status'] == 'inactivo':
            return {
                'statusCode': 403,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({"error_message": "Usuario inactivo."})
            }


        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': role
            })
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({"error_message": str(e)})
        }