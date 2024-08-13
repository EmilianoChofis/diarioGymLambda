import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

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


def lambda_handler(event, __):
    client = boto3.client('cognito-idp', region_name='us-east-1')
    user_pool_id = os.getenv('USER_POOL_ID')
    client_id = os.getenv('CLIENT_ID')
    try:
        # Parsea el body del evento
        body_parameters = json.loads(event["body"])
        username = body_parameters.get('username')
        temporary_password = body_parameters.get('temporary_password')
        new_password = body_parameters.get('new_password')

        if not username or not temporary_password or not new_password:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,PATCH'
                },
                'body': json.dumps({"error_message": "Campos faltantes."})
            }

        # Verifica que el usuario exista en Cognito
        if not user_exists_in_cognito(username):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,PATCH'
                },
                'body': json.dumps({"error_message": "El usaurio no existe."})
            }


        # Autentica al usuario con la contraseña temporal
        response = client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': temporary_password
            }
        )

        if response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
            client.respond_to_auth_challenge(
                ClientId=client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=response['Session'],
                ChallengeResponses={
                    'USERNAME': username,
                    'NEW_PASSWORD': new_password,
                    'email_verified': 'true'
                }
            )
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,PATCH'
                },
                'body': json.dumps({"message": "Cambio de contraseña correcto."})
            }
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,PATCH'
                },
                'body': json.dumps({"message": "Error al cambiar la contraseña."})
            }

    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,PATCH'
            },
            'body': json.dumps({"message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,PATCH'
            },
            'body': json.dumps({"message": str(e)})
        }
