import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from botocore.exceptions import ClientError
from routines.feedback.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    @patch('routines.feedback.app.get_routine')
    @patch('routines.feedback.app.user_has_team')
    @patch('routines.feedback.app.user_is_in_group')
    @patch('routines.feedback.app.register_feedback')
    def test_successful_feedback(self, mock_register_feedback, mock_user_is_in_group, mock_user_has_team, mock_get_routine, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        #simulacion de registro de feedback
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_routine.return_value = {'userId': '123'}
        mock_user_has_team.return_value = {'id': 'team1'}
        mock_user_is_in_group.return_value = True
        mock_register_feedback.return_value = 1  # Éxito en el registro

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Feedback registrado exitosamente.")

    @patch('routines.feedback.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #test token invalido, probablemente se preguntara, pq hay tantas formas de validar el token
        #dentro de nuestro proyecto, y la verdad yo tambien, cada test que hago tengo que cambiar la forma
        #de hacer el mock y ya me estoy hartando gracias
        mock_validate_token.return_value = (None, 'Token inválido.')

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], 'Token inválido.')

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    def test_invalid_role(self, mock_validate_user_role, mock_validate_token):
        #test con rol de user, no deberia dejar registrar feedbacks
        mock_validate_token.return_value = ({'cognito:groups': ['User']}, None)
        mock_validate_user_role.return_value = False

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    def test_missing_body(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
#tes tsin body
        event = {
            'body': {}
        }
        #test fallido
        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    def test_missing_parameters(self, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        #test sin propiedades importantes
        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                #body sin routineId, score y comment
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Los campos couchUid, routineId, score y comment son requeridos.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    @patch('routines.feedback.app.get_routine')
    def test_user_not_found(self, mock_get_routine, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        #test con usuario inexistente en la base de datos
        mock_user_exists_in_db.return_value = False

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    @patch('routines.feedback.app.get_routine')
    def test_routine_not_found(self, mock_get_routine, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        #test con rutina no existente en base de datos o no encontrada como lo quieran ver
        mock_get_routine.return_value = None

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ninguna rutina con ese id.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    @patch('routines.feedback.app.get_routine')
    @patch('routines.feedback.app.user_has_team')
    def test_no_team(self, mock_user_has_team, mock_get_routine, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_routine.return_value = {'userId': '123'}
        #test con un usuario sin equipo
        mock_user_has_team.return_value = None

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "El couch no tiene un equipo registrado.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    @patch('routines.feedback.app.get_routine')
    @patch('routines.feedback.app.user_has_team')
    @patch('routines.feedback.app.user_is_in_group')
    def test_user_not_in_team(self, mock_user_is_in_group, mock_user_has_team, mock_get_routine, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_routine.return_value = {'userId': '123'}
        mock_user_has_team.return_value = {'id': 'team1'}
        #test con usuario con grupo pero no el del couch que esta calificando
        mock_user_is_in_group.return_value = False

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "El usuario no pertenece al equipo del couch.")

    @patch('routines.feedback.app.validate_token')
    @patch('routines.feedback.app.validate_user_role')
    @patch('routines.feedback.app.user_exists_in_db')
    @patch('routines.feedback.app.get_routine')
    @patch('routines.feedback.app.user_has_team')
    @patch('routines.feedback.app.user_is_in_group')
    @patch('routines.feedback.app.register_feedback')
    def test_feedback_registration_error(self, mock_register_feedback, mock_user_is_in_group, mock_user_has_team, mock_get_routine, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_routine.return_value = {'userId': '123'}
        mock_user_has_team.return_value = {'id': 'team1'}
        mock_user_is_in_group.return_value = True
        #Test con error a la hora de ya registrar en base
        mock_register_feedback.return_value = 0

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "No se pudo registrar el feedback. Intente de nuevo.")

    @patch('routines.feedback.app.validate_token')
    def test_client_error(self, mock_validate_token):
        #test cline erro
        mock_validate_token.side_effect = ClientError({'Error': {'Message': 'Client error'}}, 'Operation')

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error en la conexión. An error occurred (Unknown) when calling the Operation operation: Client error")

    @patch('routines.feedback.app.validate_token')
    def test_general_exception(self, mock_validate_token):
        #test excepcion generica
        mock_validate_token.side_effect = Exception('General error')

        event = {
            'body': json.dumps({
                'couchUid': 'Joksan1231',
                'routineId': 'Pecho',
                'score': 5,
                'comment': 'Wow, pasado de burger pokito mas y eres arnold swcharsenegger!'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. General error")

if __name__ == '__main__':
    unittest.main()
