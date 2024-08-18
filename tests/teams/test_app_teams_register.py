import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.register.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.insert_team_db')
    def test_lambda_handler_successful_registration(self, mock_insert_team_db, mock_user_has_team, mock_user_exists_in_db,mock_validate_user_role, mock_validate_token):
        #test todo correcto
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False
        mock_insert_team_db.return_value = "equipo1231"

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], "Equipo registrado correctamente.")
        self.assertEqual(json.loads(response['body'])['data']['id'], "equipo1231")

    @patch('teams.register.app.validate_token')
    def test_lambda_handler_invalid_token(self, mock_validate_token):
        #test token invalido
        mock_validate_token.return_value = (None, "Token inválido")

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "Token inválido")

    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    def test_lambda_handler_invalid_role(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        #test role invalido
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.insert_team_db')
    def test_lambda_handler_missing_body(self, mock_insert_team_db, mock_user_has_team, mock_user_exists_in_db,mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False
        mock_insert_team_db.return_value = "equipo1231"
        #body vacio
        event = {
            "body":json.dumps({})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.insert_team_db')
    def test_lambda_handler_missing_body(self, mock_insert_team_db, mock_user_has_team, mock_user_exists_in_db,mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False
        mock_insert_team_db.return_value = "equipo1231"
        #body sin el id del coach dentro
        event = {
            "body":json.dumps({"otrocampo": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "EL campo couchId es requerido.")

    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    def test_lambda_handler_user_not_found(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        #test usuario no encontrado
        mock_user_exists_in_db.return_value = False

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")

    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    def test_lambda_handler_user_has_team(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db, mock_user_has_team):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        #test coach ya cuenta con un equipo
        mock_user_has_team.return_value = True

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "El couch ya tiene un equipo creado.")

    @patch('teams.register.app.insert_team_db')
    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    def test_lambda_handler_team_registration_failure(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db, mock_user_has_team, mock_insert_team_db):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False
        #test error al registrar el equipo
        mock_insert_team_db.return_value = None

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "No se pudo registrar el equipo.")

    @patch('teams.register.app.logging.error')
    @patch('teams.register.app.insert_team_db')
    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    def test_lambda_handler_client_error(self, mock_validate_user_role, mock_validate_token,mock_user_exists_in_db, mock_user_has_team, mock_insert_team_db, mock_logging_error):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False
        #test disparar el client errorr
        mock_insert_team_db.side_effect = ClientError({"Error": {"Code": "500", "Message": "Client error"}}, "Insert")

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error en la conexión. An error occurred (500) when calling the Insert operation: Client error")

    @patch('teams.register.app.logging.error')
    @patch('teams.register.app.insert_team_db')
    @patch('teams.register.app.user_has_team')
    @patch('teams.register.app.user_exists_in_db')
    @patch('teams.register.app.validate_token')
    @patch('teams.register.app.validate_user_role')
    def test_lambda_handler_unhandled_exception(self, mock_validate_user_role, mock_validate_token,mock_user_exists_in_db, mock_user_has_team, mock_insert_team_db,mock_logging_error):
        mock_validate_token.return_value = ({"sub": "123"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False
        #test disparamos un error cualquiera
        mock_insert_team_db.side_effect = Exception("Exception cualquiera")

        event = {
            "body": json.dumps({"couchUid": "Coquito1231"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Exception cualquiera")


if __name__ == '__main__':
    unittest.main()
