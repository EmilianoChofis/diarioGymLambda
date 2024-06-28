import json
from db_conn import connect_to_db
import jwt


def lambda_handler(event, __):
    body = json.loads(event["body"])
    header = json.loads(event["headers"])

    id_token = header.get('Authorization')

    if not id_token:
        return {
            'statusCode': 401,
            'body': json.dumps({
                "message": "No autorizado."
            })
        }

    try:
        claims = jwt.decode(id_token, options={"verify_signature": False})
    except Exception as e:
        return {
            'statusCode': 401,
            'body': json.dumps({
                "message": "Error al verificar token" + str(e)
            })
        }

    if 'cognito:groups' in claims:
        role = claims['cognito:groups']

        if 'administradores' not in role:
            return {
                'statusCode': 403,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

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
