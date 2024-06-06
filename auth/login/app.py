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


def lambda_handler(event, __):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps('Petición inválida. no se encontró el body.')
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
