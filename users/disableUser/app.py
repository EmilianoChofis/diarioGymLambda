import json
from db_conn import connect_to_db
import jwt


def lambda_handler(event, __):
    try:
        body = json.loads(event.get("body", "{}"))
        header = json.loads(event.get("headers", "{}"))
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "Error en la estructura del JSON: " + str(e)
            })
        }

    id_token = header.get('Authorization')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El body es requerido para la petición."
            })
        }

    user_id = body.get('id')

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

    try:
        connection = connect_to_db()
        if connection is None:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde."
                })
            }

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
                'message': "Error de servidor. Vuelve a intentarlo más tarde. " + str(e)
            })
        }

    finally:
        if connection:
            connection.close()
