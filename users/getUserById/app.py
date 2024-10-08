import json
import logging

from botocore.exceptions import ClientError
from db_conn import connect_to_db


def lambda_handler(event, __):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                "message": "El body es requerido para la petición."
            })
        }

    data = json.loads(body)

    userUid = data.get('userUid')
    connection = connect_to_db()

    if connection is None:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                "message": "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde."
            })
        }

    if not userUid:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                "message": "El campo userUid es requerido."
            })
        }

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE uid = %s"
            cursor.execute(sql, (userUid,))
            result = cursor.fetchone()
            connection.commit()
            if result:
                response = {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': 'true',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        "message": "Usuario encontrado",
                        "data": result
                    })
                }
            else:
                response = {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': 'true',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps(
                        {
                            'message': 'Usuario no encontrado.'
                        }
                    )
                }

            return response

    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'message': f"Error en la conexión. {e}"
            })
        }

    except Exception as e:
        logging.error(f"Error: ${e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error de servidor. Vuelve a intentarlo más tarde."
            })
        }

    finally:
        connection.close()
