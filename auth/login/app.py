import json
import os
import pymysql
import boto3
from botocore.exceptions import ClientError


def get_secret():
    secret_name = "dev/ute/mysqlSecrets"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"ERROR: Unexpected error: Could not to get secrets. {e}")
        raise e

    secret = get_secret_value_response['SecretString']
    return secret


# Conexión a la base de datos
def connect_to_db():
    secret = json.loads(get_secret())

    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=secret['username'],
            password=secret['password'],
            database=os.getenv('DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"ERROR: Unexpected error: Could not connect to MySQL instance. {e}")
        return None


def lambda_handler(event, __):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps('invalid petition. no se encontró el body.')
        }

    data = json.loads(body)

    username = data.get('email')
    password = data.get('password')

    if not username or not password:
        return {
            'statusCode': 400,
            'body': json.dumps('Faltan datos para el login.')
        }

    connection = connect_to_db()
    if connection is None:
        return {
            'statusCode': 500,
            'body': json.dumps('No se pudo conectar a la base de datos.')
        }

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s AND password = %s"
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
