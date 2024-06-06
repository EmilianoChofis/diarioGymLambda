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

    """
    :param event:
    :param __:
    :return:
    """

    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps('Petición inválida. no se encontró el body.')
        }

    data = json.loads(body)

    user_id = data.get('id')
    connection = connect_to_db()

    try:
        with connection.cursor() as cursor:
            sql = "SELECT username, email, role_id, enable FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            connection.commit()
            if result:
                response = {
                    'statusCode': 200,
                    'body': json.dumps(result)
                }
            else:
                response = {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'User not found'})
                }

            return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

    finally:
        connection.close()
