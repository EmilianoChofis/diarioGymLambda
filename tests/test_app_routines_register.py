import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from routines.register.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    @patch('routines.register.app.user_exists_in_db')
    @patch('routines.register.app.routine_exists_today')
    @patch('routines.register.app.register_routine_exercise')
    @patch('routines.register.app.exercise_exists')
    def test_successful_routine_registration(self, mock_exercise_exists, mock_register_routine_exercise, mock_routine_exists_today, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        # Todo correcto
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_routine_exists_today.return_value = False
        mock_exercise_exists.return_value = True
        mock_register_routine_exercise.return_value = "rutina123"

        event = {
            'body': json.dumps({
                'user': {'uid': 'coquito123'},
                'date': '2001-12-26',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], "Rutina registrada correctamente.")
        self.assertIn('data', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['data']['id'], "rutina123")

    @patch('routines.register.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #Token invalido
        mock_validate_token.return_value = (None, 'Token inválido.')

        event = {
            'body': json.dumps({
                'user': {'uid': 'coquito123'},
                'date': '2001-12-26',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], 'Token inválido.')

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    def test_invalid_role(self, mock_validate_user_role, mock_validate_token):
        #test rol sin permisos
        mock_validate_token.return_value = ({'cognito:groups': ['User']}, None)
        mock_validate_user_role.return_value = False

        event = {
            'body': json.dumps({
                'user': {'uid': 'coquito123'},
                'date': '2001-12-26',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('routines.register.app.validate_token')
    def test_missing_body(self, mock_validate_token):
        #test sin body
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)

        event = {
            'body': json.dumps({})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('routines.register.app.validate_token')
    def test_missing_user(self, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        #test sin campos obligatorios
        event = {
            'body': json.dumps({
                #quitamos user
                #'user': {'uid': 'coquito123'},
                'date': '2001-12-26',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "EL campo user es requerido.")

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.user_exists_in_db')
    def test_user_not_found(self, mock_user_exists_in_db, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        #test usuario no encontrado
        mock_user_exists_in_db.return_value = False

        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró el usuario.")

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    @patch('routines.register.app.user_exists_in_db')
    @patch('routines.register.app.routine_exists_today')
    def test_routine_exists(self, mock_routine_exists_today,mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        #test la rutina ya fue registrada hoy
        mock_routine_exists_today.return_value = True

        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Ya existe una rutina registrada para este día.")

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    @patch('routines.register.app.user_exists_in_db')
    @patch('routines.register.app.routine_exists_today')
    @patch('routines.register.app.register_routine_exercise')
    @patch('routines.register.app.exercise_exists')
    def test_exercise_not_found(self, mock_exercise_exists, mock_register_routine_exercise, mock_routine_exists_today, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_routine_exists_today.return_value = False
        #test ejercicio no encontrado
        mock_exercise_exists.return_value = False
        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró el ejercicio.")

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    @patch('routines.register.app.user_exists_in_db')
    @patch('routines.register.app.routine_exists_today')
    @patch('routines.register.app.register_routine_exercise')
    @patch('routines.register.app.exercise_exists')
    def test_invalid_exercise_reps(self, mock_exercise_exists, mock_register_routine_exercise, mock_routine_exists_today, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_routine_exists_today.return_value = False
        mock_exercise_exists.return_value = True
        mock_register_routine_exercise.return_value = "rutina123"

        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                #test reps = 0
                'exercises': [{'id': 'levantaGluteos1', 'reps': 0, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El campo reps debe ser mayor a 0.")

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    @patch('routines.register.app.user_exists_in_db')
    @patch('routines.register.app.routine_exists_today')
    @patch('routines.register.app.register_routine_exercise')
    @patch('routines.register.app.exercise_exists')
    def test_invalid_exercise_sets(self, mock_exercise_exists, mock_register_routine_exercise, mock_routine_exists_today, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_routine_exists_today.return_value = False
        mock_exercise_exists.return_value = True
        mock_register_routine_exercise.return_value = "rutina123"
        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                #test sets=0
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 0}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El campo sets debe ser mayor a 0.")

    @patch('routines.register.app.validate_token')
    @patch('routines.register.app.validate_user_role')
    @patch('routines.register.app.user_exists_in_db')
    @patch('routines.register.app.routine_exists_today')
    @patch('routines.register.app.register_routine_exercise')
    @patch('routines.register.app.exercise_exists')
    def test_routine_registration_failure(self, mock_exercise_exists, mock_register_routine_exercise, mock_routine_exists_today, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_routine_exists_today.return_value = False
        mock_exercise_exists.return_value = True
        #eeror al registrar un ejercicio
        mock_register_routine_exercise.return_value = None

        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "No se pudo registrar la rutina.")

    @patch('routines.register.app.validate_token')
    def test_client_error(self, mock_validate_token):
        #test disparamos el client error
        mock_validate_token.side_effect = ClientError({'Error': {'Message': 'Client error'}}, 'Operation')

        event = {
            'body': json.dumps({
                'user': {'uid': 'user123'},
                'date': '2024-08-16',
                'exercises': [{'id': 'levantaGluteos1', 'reps': 10, 'sets': 3}]
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error en la conexión. An error occurred (Unknown) when calling the Operation operation: Client error")

if __name__ == '__main__':
    unittest.main()