import json

import boto3
from botocore.exceptions import ClientError


def generate_temporary_password():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


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

    if email is None or username is None or name is None or lastname is None or age is None or gender is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Faltan campos requeridos."})
        }

    try:
        # Configura el cliente de Cognito
        client = boto3.client('cognito-idp', region_name='us-east-1')
        user_pool_id = "us-east-1_1HAjH1fKj"

        # Crea el usuario con correo no verificado y contraseña temporal que se envia automaticamente a su correo
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
        #insertar en la db
        #insert_db(email, username, name, age, gender, password)

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "User created successfully, verification email sent."})
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error_message": str(e)})
        }


