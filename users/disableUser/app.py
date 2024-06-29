import json
from db_conn import connect_to_db
import jwt


def lambda_handler(event, __):
    body = event.get('body')

    token = event.get('headers')
    data = json.loads(token)
    access_token = data.get('Authorization')

    if not access_token:
        return {
            'statusCode': 401,
            'body': json.dumps({
                "message": "No tienes permisos para realizar esta acción."
            })
        }

    claims = jwt.decode(access_token, options={"verify_signature": False})
    print(claims)
    #admin
    role = None
    if 'cognito:groups' in claims:
        role = claims['cognito:groups']
        print(role)

    if role is None or role[0] != 'administradores':
        return {
            'statusCode': 401,
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
            sql = "UPDATE users SET expire_at = CURRENT_TIMESTAMP, enable = '0' WHERE id = %s"
            cursor.execute(sql, (userId,))
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
                'message': "Error de servidor. Vuelve a intentarlo más tarde."
            })
        }

    finally:
        connection.close()
