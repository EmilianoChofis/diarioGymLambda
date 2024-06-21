import json
import pymysql
from db_conn import connect_to_db


def lambda_handler(event, __):
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
            'body': json.dumps({
                "message": "El campo id es requerido."
            })
        }

    if not isinstance(user_id, int):
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El campo id debe ser un número."
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
            # Verificar si el usuario existe
            sql = "SELECT * FROM users_inc WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if not result:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        "message": "Usuario no encontrado."
                    })
                }

            # Actualizar la información del usuario
            update_fields = []
            update_values = []

            if not username and not password and not email and not role:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        "message": "No se recibieron datos para actualizar."
                    })
                }

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
            sql = f"UPDATE users_inc SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(sql, update_values)
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Usuario actualizado correctamente.",
                "data": {
                    "id": user_id,
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
