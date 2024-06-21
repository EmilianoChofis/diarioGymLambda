import json
import pymysql

from auth.login.db_conn import connect_to_db


def lambda_handler(event, __):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El body es requerido para la petición."
            })
        }

    data = json.loads(body)

    username = data.get('email')
    password = data.get('password')

    if not username or not password:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "Los campos email y password son requeridos."
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

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users_inc WHERE email = %s AND password = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()

            if result:
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        "message": "Login exitoso",
                        "data": {
                            "token": "sin token pa"
                        }
                    })
                }
            else:
                return {
                    'statusCode': 401,
                    'body': json.dumps({
                        "message": "Credenciales inválidas."
                    })
                }

    except pymysql.MySQLError as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error de servidor. Vuelve a intentarlo más tarde."
            })
        }

    finally:
        connection.close()
