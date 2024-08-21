import json
import logging
import os
import random
import string

import boto3
from botocore.exceptions import ClientError

from .queries import user_exists_in_cognito, email_exists_in_cognito, insert_user_pool, insert_user_db
from .validate_token import validate_token, validate_user_role


def generate_temporary_password(length=12):
    special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+='
    characters = string.ascii_letters + string.digits + special_characters

    while True:
        # Genera una contraseña aleatoria
        password = ''.join(random.choice(characters) for _ in range(length))

        # Verifica los criterios
        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in special_characters for char in password)

        if has_digit and has_upper and has_lower and has_special and len(password) >= 8:
            return password


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
    try:

        claims, error_message = validate_token(event)

        if error_message:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": error_message
                })
            }

        if not validate_user_role(claims, ['Admin']):
            return {
                'statusCode': 403,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        body_parameters = json.loads(event["body"])

        if not body_parameters:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": "El body es requerido para la petición."
                })
            }

        email = body_parameters.get('email')
        username = body_parameters.get('username')
        name = body_parameters.get('name')
        lastname = body_parameters.get('lastname')
        age = body_parameters.get('age')
        gender = body_parameters.get('gender')
        password = generate_temporary_password()
        role = body_parameters.get('role')

        if (email is None or username is None or name is None or lastname is None or age is None
                or gender is None or role is None):
            return {
                "statusCode": 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                "body": json.dumps({"message": "Faltan campos requeridos."})
            }

        if role not in ['Admin', 'User', 'Couch']:
            return {
                "statusCode": 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                "body": json.dumps({"message": "El rol no es válido."})
            }

        if user_exists_in_cognito(username):
            return {
                'statusCode': 409,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": "El usuario ya se encuentra registrado."
                })
            }

        if email_exists_in_cognito(email):
            return {
                'statusCode': 409,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": "El correo ya se encuentra registrado."
                })
            }

        insert_user_pool(email, username, password, role)
        uid = get_user_id_by_username(username)
        insert_user_db(uid, name, lastname, age, gender)

        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                "message": "Usuario registrado correctamente.",
            })
        }

    except ResourceNotFound as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'message': f"Recurso no encontrado. {e}"
            })
        }

    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'message': f"Error en la conexión. {e}"
            })
        }

    except Exception as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'message': f"Error de servidor. {e}"
            })
        }
