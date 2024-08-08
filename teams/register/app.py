import json
import logging
from botocore.exceptions import ClientError

from teams.register.insert_user_db import user_exists_in_db, insert_team_db, user_has_team
from teams.register.validate_token import validate_token, validate_user_role


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

        if not validate_user_role(claims, ['Couch', 'Admin']):
            return {
                'statusCode': 401,
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

        couchUid = body_parameters.get("couchUid")

        if couchUid is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo couchId es requerido."})
            }

        if user_exists_in_db(couchUid) is False:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No se encontró ningun usuario con ese uid."
                })
            }

        if user_has_team(couchUid):
            return {
                'statusCode': 409,
                'body': json.dumps({
                    "message": "El couch ya tiene un equipo creado."
                })
            }

        teamId = insert_team_db(couchUid)

        if teamId is None:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "No se pudo registrar el equipo."
                })
            }

        return {
            'statusCode': 201,
            'body': json.dumps({
                "message": "Usuario registrado correctamente.",
                "data": {
                    "couchUid": couchUid

                }
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
