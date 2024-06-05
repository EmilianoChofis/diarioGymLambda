import json


def lambda_handler(event, context):
    username = event.get('username')
    password = event.get('password')
    email = event.get('email')
    role = event.get('role')

    if not username or not password or not email or not role:
        return {
            'statusCode': 400,
            'body': json.dumps('Faltan datos para el registro.')
        }

    connection = connect_to_db()
    if connection is None:
        return {
            'statusCode': 500,
            'body': json.dumps('No se pudo conectar a la base de datos.')
        }

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s OR email = %s"
            cursor.execute(sql, (username, email))
            result = cursor.fetchone()
            if result:
                return {
                    'statusCode': 409,
                    'body': json.dumps('El usuario o email ya existen.')
                }

            # Insertar nuevo usuario
            sql = "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, password, email, role))
            connection.commit()

        return {
            'statusCode': 201,
            'body': json.dumps('Usuario registrado exitosamente.')
        }

    except pymysql.MySQLError as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error en el servidor al registrar el usuario.')
        }

    finally:
        connection.close()
