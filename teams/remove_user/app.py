import json
import logging
from botocore.exceptions import ClientError

from queries import user_exists_in_db, user_has_team, get_couch_team, remove_user_team
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

        if not validate_user_role(claims, ['Couch']):
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

        couch = body_parameters.get("couch")

        if couch is None:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "El campo couch es requerido."
                })
            }

        couchId = couch.get("uid")

        if couchId is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo uid del couch es requerido."})
            }

        user = body_parameters.get("user")

        if user is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo user es requerido."})
            }

        userId = user.get("uid")

        if userId is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo user.uid es requerido."})
            }

        couchTeam = get_couch_team(couchId)

        if couchTeam is None:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "El couch no cuenta con ningun equipo registrado."
                })
            }

        if user_exists_in_db(userId) is False:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No se encontró ningun usuario con ese uid."
                })
            }

        if user_has_team(userId, couchTeam.get("id")) is False:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "El usuario no pertenece al equipo del couch."
                })
            }

        isDeleted = remove_user_team(userId, couchTeam.get("id"))

        if isDeleted is None:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "No se pudo eliminar al usuario del equipo."
                })
            }

        return {
            'statusCode': 201,
            'body': json.dumps({
                "message": "Usuario eliminado del equipo correctamente.",
            })
        }

    except ClientError as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Error en la conexión. {e}"
            })
        }

    except Exception as e:
        logging.error(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error de servidor. {e}"
            })
        }
