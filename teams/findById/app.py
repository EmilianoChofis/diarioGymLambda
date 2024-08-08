import json
import logging
from botocore.exceptions import ClientError

from teams.findById.queries import get_team_by_id
from teams.findById.validate_token import validate_token, validate_user_role


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

        if not validate_user_role(claims, ['Couch', 'Admin', 'User']):
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

        id = body_parameters.get("id")

        if id is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "El campo id es requerido."})
            }

        team = get_team_by_id(id)

        if team is None:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No existe ningun equipo con ese id"
                })
            }

        return {
            'statusCode': 201,
            'body': json.dumps({
                "message": "Usuario registrado correctamente.",
                "data": team
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
