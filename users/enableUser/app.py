import json
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

    userId = data.get('id')

    if not userId:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "message": "El campo id es requerido."
            })
        }

    if not isinstance(userId, int):
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
            sql = "UPDATE users_inc SET expire_at = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 30 DAY), enable = '1' WHERE id = %s"
            cursor.execute(sql, (userId,))
            connection.commit()
            response = {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Usuario habilitado correctamente',
                })
            }
            return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error de servidor. Vuelve a intentarlo más tarde."
            })
        }

    finally:
        connection.close()
