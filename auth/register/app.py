import json
import pymysql
from db_conn import connect_to_db


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

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role')

    if not username or not password or not email or not role:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "Los campos username, password, email y role son requeridos."
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

    if role not in ["admin", "user"]:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El campo role debe ser 'admin' o 'user'."
            })
       }

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s OR email = %s"
            cursor.execute(sql, (username, email))
            result = cursor.fetchone()
            if result:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        "message": "El usuario ya existe."
                    })
                }

            sql = "INSERT INTO users (username, password, email, role_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, password, email, role))
            connection.commit()

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
