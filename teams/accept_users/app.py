import json
import logging
from botocore.exceptions import ClientError

from queries import user_exists_in_db, user_has_team, number_of_members, insert_user_group, get_team_by_id
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

        if not validate_user_role(claims, ['User', 'Admin']):
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

        team = body_parameters.get("team")

        if team is None:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "El campo team es requerido."
                })
            }

        teamId = team.get("id")

        if teamId is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo couchId es requerido."})
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

        if user_exists_in_db(userId) is False:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No se encontró ningun usuario con ese uid."
                })
            }

        if get_team_by_id(teamId) is None:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No se encontró ningun equipo con ese id."
                })
            }

        if user_has_team(userId):
            return {
                'statusCode': 409,
                'body': json.dumps({
                    "message": "El usuario ya tiene un equipo asignado."
                })
            }

        membersOfTeam = number_of_members(teamId)

        if membersOfTeam > 7:
            return {
                'statusCode': 409,
                'body': json.dumps({
                    "message": "El equipo ya tiene el número máximo de integrantes."
                })
            }

        isRegistered = insert_user_group(userId, teamId)

        if isRegistered is None:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "No se pudo agregar el usuario al equipo."
                })
            }

        return {
            'statusCode': 201,
            'body': json.dumps({
                "message": "Usuario agregado al equipo correctamente.",
                "data": {
                    "user_id": userId,
                    "team_id": teamId
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
