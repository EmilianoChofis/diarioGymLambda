import json
from db_conn import connect_to_db
import jwt


def lambda_handler(event, __):
    try:
        body = event.get('body')
        headers = event.get('headers')

        if headers is None:
            return {
                'statusCode': 401,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        access_token = headers.get('Authorization')

        if not access_token or not access_token.startswith("Bearer "):
            return {
                'statusCode': 401,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        access_token = access_token.split(" ")[1]

        claims = jwt.decode(access_token, options={"verify_signature": False})
        print(claims)

        # Validar rol
        role = claims.get('cognito:groups')
        print(role)

        if not role or 'administradores' not in role:
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
            print(f"Error al ejecutar la consulta: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': "Error de servidor. Vuelve a intentarlo más tarde."
                })
            }

        finally:
            connection.close()
    except Exception as e:
        print(f"Error en lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error interno del servidor."
            })
        }
