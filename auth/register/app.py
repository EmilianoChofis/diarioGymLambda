import json
import logging
import random
import string

from botocore.exceptions import ClientError

from insert_user_db import insert_user_db
from insert_user_pool import insert_user_pool


def generate_temporary_password(length=12):
    special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= '
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

def lambda_handler(event, __):
    body_parameters = json.loads(event["body"])
    email = body_parameters.get('email')
    username = body_parameters.get('username')
    name = body_parameters.get('name')
    lastname = body_parameters.get('lastname')
    age = body_parameters.get('age')
    gender = body_parameters.get('gender')
    password = generate_temporary_password()
    role = body_parameters.get('role', 'User')

    if not body_parameters:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El body es requerido para la petición."
            })
        }

    if email is None or username is None or name is None or lastname is None or age is None or gender is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Faltan campos requeridos."})
        }

    try:
        insert_user_pool(email, username, password, role)
        uid = '123abcd'
        insert_user_db(uid, name, lastname, age, gender)
        return {
            'statusCode': 201,
            'body': json.dumps({
                "message": "Usuario registrado correctamente.",
                "data": {
                    "username": username,
                    "email": email,
                    "role": role
                }
            })
        }
    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Error de servidor. {e}"
            })
        }
    except Exception as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error de servidor. {e}"
            })
        }
