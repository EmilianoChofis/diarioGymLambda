import json
import logging

import jwt
from botocore.exceptions import ClientError

from db_conn import connect_to_db


def lambda_handler(event, __):
    try:
        headers = event.get('headers')

        if headers is None:
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'message': "No tienes permisos para realizar esta acción."
                })
            }

        access_token = headers.get('Authorization')

        if not access_token or not access_token.startswith("Bearer "):
            return {
                'statusCode': 401,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        access_token = access_token.split(" ")[1]

        claims = jwt.decode(access_token, options={
            "verify_signature": False
        })
        logging.info(f"${claims}")

        role = claims.get('cognito:groups')
        logging.info(f"${role}")

        if not role or 'Admin' not in role:
            return {
                'statusCode': 401,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        connection = connect_to_db()

        if connection is None:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde."
                })
            }

        with connection.cursor() as cursor:
            sql = "SELECT * FROM users_inc"
            cursor.execute(sql)
            result = cursor.fetchall()
            connection.commit()

            if result:
                response = {
                    'statusCode': 200,
                    'body': json.dumps({
                        "message": "Lista de usuarios obtenidos",
                        "data": result
                    })
                }
            else:
                response = {
                    'statusCode': 404,
                    'body': json.dumps({
                        'message': 'No se encontraron usuarios'
                    })
                }

            return response

    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Error en la conexión. {e}"
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