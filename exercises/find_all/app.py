import json
import pymysql
from db_conn import connect_to_db

def validate_user(connection, user_id):
    with connection.cursor() as cursor:
        sql = "SELECT role_id FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result and result['role_id'] in ['admin', 'user']:
            return True
        return False

def lambda_handler(event, context):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El body es requerido para la petición."
            })
        }

    data = json.loads(body)
    created_by = data.get('created_by')

    if not created_by:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El campo created_by es requerido."
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
        if not validate_user(connection, created_by):
            return {
                'statusCode': 403,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        with connection.cursor() as cursor:
            sql = "SELECT * FROM exercises"
            cursor.execute(sql)
            result = cursor.fetchall()
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "message": "Consulta exitosa.",
                    "data": result
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
