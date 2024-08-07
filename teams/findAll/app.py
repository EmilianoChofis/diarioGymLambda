import json
import logging
from botocore.exceptions import ClientError

from queries import get_teams
from validate_token import validate_token, validate_user_role


def lambda_handler(event, __):
    try:
        # Validar el token y obtener los claims
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
                'statusCode': 403,
                'body': json.dumps({
                    "message": "No tienes permisos para realizar esta acción."
                })
            }

        teams = get_teams()

        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Lista de equipos registrados.",
                "data": teams,
                "total": len(teams)
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