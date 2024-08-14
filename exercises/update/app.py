import json
import pymysql
from .db_conn import connect_to_db
import jwt


def lambda_handler(event, __):
    try:
        body = event.get('body')
        headers = event.get('headers')

        if headers is None:
            return {
                'statusCode': 401,
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

        access_token = headers.get('Authorization')

        if not access_token or not access_token.startswith("Bearer "):
            return {
                'statusCode': 401,
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

        access_token = access_token.split(" ")[1]

        claims = jwt.decode(access_token, options={"verify_signature": False})
        print(claims)

        # Validar rol
        role = claims.get('cognito:groups')
        print(role)

        if not role or 'Admin' not in role:
            return {
                'statusCode': 401,
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

        if not body:
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

        data = json.loads(body)
        exercise_id = data.get('exercise_id')
        name = data.get('name')
        description = data.get('description')

        if  not exercise_id or not name or not description:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": "Los campos exercise_id, name y description son requeridos."
                })
            }

        connection = connect_to_db()
        if connection is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    "message": "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde."
                })
            }

        try:
            with connection.cursor() as cursor:
                sql = "UPDATE exercises SET name = %s, description = %s WHERE id = %s"
                cursor.execute(sql, (name, description, exercise_id))
                connection.commit()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': 'true',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST'
                    },
                    'body': json.dumps({
                        "message": "Ejercicio actualizado exitosamente."
                    })
                }

        except pymysql.MySQLError as e:
            print(f"ERROR: {e}")
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({
                    'message': "Error de servidor. Vuelve a intentarlo más tarde."
                })
            }

        finally:
            connection.close()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'message': "Error de servidor. Vuelve a intentarlo más tarde."
            })
        }
