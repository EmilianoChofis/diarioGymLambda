import json
import pymysql

# Configuración de la conexión a la base de datos
rds_host = "databaseforlambdas.czssy4oigfcr.us-east-1.rds.amazonaws.com"
db_username = "admin"
db_password = "admin123"
db_name = "chomfit"

# Conexión a la base de datos
def connect_to_db():
    try:
        connection = pymysql.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            database=db_name,
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
