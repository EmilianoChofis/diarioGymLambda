import json
import logging
from botocore.exceptions import ClientError

from queries import exercise_exists, register_routine_exercise, routine_exists_today, user_exists_in_db
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

        if not validate_user_role(claims, ['Couch', 'Admin', 'User']):
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

        user = body_parameters.get("user")

        if user is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo user es requerido."})
            }

        userUid = user.get("uid")

        if userUid is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo uid es requerido."})
            }

        date = body_parameters.get("date")

        if date is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo date es requerido."})
            }

        exercises = body_parameters.get("exercises")

        if exercises is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "EL campo exercises es requerido."})
            }

        if len(exercises) == 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Debe haber al menos un ejercicio."})
            }

        if not isinstance(exercises, list):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "El campo exercises debe ser una lista."})
            }

        if len (exercises) > 7:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No se pueden registrar más de 7 ejercicios."})
            }

        userExists = user_exists_in_db(userUid)

        if userExists is False:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No se encontró el usuario."})
            }

        routine_exists = routine_exists_today(userUid)

        if routine_exists:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Ya existe una rutina registrada para este día."})
            }

        for exercise in exercises:
            if exercise.get("id") is None:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El campo id es requerido en exercises."})
                }
            if exercise.get("reps") is None:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El campo reps es requerido en exercises."})
                }
            if exercise.get("sets") is None:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El campo sets es requerido en exercises."})
                }

            if exercise_exists(exercise.get("id")) is False:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"message": "No se encontró el ejercicio."})
                }

            if exercise.get("reps") <= 0:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El campo reps debe ser mayor a 0."})
                }

            if exercise.get("sets") <= 0:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El campo sets debe ser mayor a 0."})
                }

        routineId = register_routine_exercise(body_parameters)

        if routineId is None:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "message": "No se pudo registrar la rutina."
                })
            }

        return {
            'statusCode': 201,
            'body': json.dumps({
                "message": "Rutina registrada correctamente.",
                "data": {
                    "id": routineId
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
