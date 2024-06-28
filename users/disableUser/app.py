import json
from db_conn import connect_to_db
import jwt


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

    user_id = data.get('id')

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
            sql = "UPDATE users SET expire_at = CURRENT_TIMESTAMP, enable = '0' WHERE id = %s"
            cursor.execute(sql, (user_id,))
            connection.commit()
            response = {
                'statusCode': 200,
                'body': json.dumps({'message': 'Usuario deshabilitado correctamente'})
            }
            return response

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error de servidor. Vuelve a intentarlo más tarde." + str(e)
            })
        }

    finally:
        connection.close()
