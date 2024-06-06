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


def lambda_handler(event, context):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps('Petición inválida. no se encontró el body.')
        }

    data = json.loads(body)

    # Datos de entrada
    user_id = data.get('id')
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role')

    # Validar que el ID esté presente
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps('Falta el ID del usuario.')
        }

    connection = connect_to_db()
    if connection is None:
        return {
            'statusCode': 500,
            'body': json.dumps('No se pudo conectar a la base de datos.')
        }

    try:
        with connection.cursor() as cursor:
            # Verificar si el usuario existe
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if not result:
                return {
                    'statusCode': 404,
                    'body': json.dumps('Usuario no encontrado.')
                }

            # Actualizar la información del usuario
            update_fields = []
            update_values = []

            if username:
                update_fields.append("username = %s")
                update_values.append(username)
            if password:
                update_fields.append("password = %s")
                update_values.append(password)
            if email:
                update_fields.append("email = %s")
                update_values.append(email)
            if role:
                update_fields.append("role_id = %s")
                update_values.append(role)

            update_values.append(user_id)
            sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(sql, update_values)
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Usuario actualizado exitosamente.')
        }

    except pymysql.MySQLError as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error en el servidor al actualizar el usuario.')
        }

    finally:
        connection.close()
