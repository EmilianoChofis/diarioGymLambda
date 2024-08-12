import json
import logging

from botocore.exceptions import ClientError

from queries import get_user, change_status_user
from validate_token import validate_token, validate_user_role


def lambda_handler(event, __):
    try:
        claims, error_message = validate_token(event)

        if error_message:
            return {
                'statusCode': 401,
                'body': json.dumps({
                    "message": error_message
                })
            }

        if not validate_user_role(claims, ['Admin']):
            return {
                'statusCode': 403,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        body_parameters = json.loads(event["body"])

        if not body_parameters:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "El body es requerido para la petición."
                })
            }

        userId = body_parameters.get('id')

        if not userId:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "El campo id es requerido."
                })
            }

        userRegistered = get_user(userId)

        if userRegistered is None:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No se encontró ningun usuario con ese uid."
                })
            }

        # Cambiar el status del usuario a inactivo si el status actual es activo, de lo contrario cambiarlo a activo
        statusToChange = 'inactivo' if userRegistered.get('status') == 'activo' else 'activo'

        response = change_status_user(userId, statusToChange)

        if response is False:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "Error al modificar el status del usuario."
                })
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Status del usuario modificado exitosamente."
            })
        }

    except ClientError as e:
        logging.error(f"Error: ${e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Error en la conexión. {e}"
            })
        }

    except Exception as e:
        logging.error(f"Error lambda handler: ${e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error interno del servidor."
            })
        }
