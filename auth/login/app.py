import json

from utils import db_connection


def lambda_handler(event, context):
    username = event.get('email')
    password = event.get('password')

    if not username or not password:
        return {
            'statusCode': 400,
            'body': json.dumps('Faltan datos para el login.')
        }

    connection = db_connection()
    if connection is None:
        return {
            'statusCode': 500,
            'body': json.dumps('No se pudo conectar a la base de datos.')
        }

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()

            if result:
                return {
                    'statusCode': 200,
                    'body': json.dumps('Login exitoso.')
                }
            else:
                return {
                    'statusCode': 401,
                    'body': json.dumps('Credenciales incorrectas. Verifica tu email y contraseña.')
                }

    except pymysql.MySQLError as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error en el servidor al intentar el login.')
        }

    finally:
        connection.close()
