import json
import pymysql
from db_conn import connect_to_db

def validate_admin(connection, user_id):
    with connection.cursor() as cursor:
        sql = "SELECT role_id FROM users_inc WHERE id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result and result['role_id'] == 'admin':
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
    name = data.get('name')
    description = data.get('description')

    if not created_by or not name or not description:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "Los campos created_by, name y description son requeridos."
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
        if not validate_admin(connection, created_by):
            return {
                'statusCode': 403,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        with connection.cursor() as cursor:
            sql = "INSERT INTO exercises_inc (name, description, created_by) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, description, created_by))
            connection.commit()
            return {
                'statusCode': 201,
                'body': json.dumps({
                    "message": "Ejercicio creado exitosamente."
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
