import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.findByUser.app import lambda_handler  # Actualiza con el nombre correcto de tu módulo


class TestLambdaHandler(unittest.TestCase):

    @patch('teams.findByUser.app.get_team_from_user')
    @patch('teams.findByUser.app.get_user')
    @patch('teams.findByUser.app.validate_user_role')
    @patch('teams.findByUser.app.validate_token')
    def test_successful_team_retrieval(self, mock_validate_token, mock_validate_user_role, mock_get_user, mock_get_team_from_user):
        #test todo correcto
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {"userUid": "user123"}
        mock_get_team_from_user.return_value = {"teamId": "equipo123", "teamName": "Equipo de Chombo"}

        event = {
            "body": json.dumps({"userUid": "user123"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn("Equipo encontrado", response['body'])
        self.assertIn("equipo123", response['body'])
        self.assertIn("Equipo de Chombo", response['body'])

    @patch('teams.findByUser.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        mock_validate_token.return_value = (None, "Token invalido")

        event = {
            "body": json.dumps({"userUid": "user123"})
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 401)
        self.assertIn("Token invalido", response['body'])


    @patch('teams.findByUser.app.get_team_from_user')
    @patch('teams.findByUser.app.get_user')
    @patch('teams.findByUser.app.validate_user_role')
    @patch('teams.findByUser.app.validate_token')
    def test_missing_body(self, mock_validate_token, mock_validate_user_role, mock_get_user, mock_get_team_from_user):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {"userUid": "user123"}
        mock_get_team_from_user.return_value = {"teamId": "equipo123", "teamName": "Equipo de Chombo"}

        event = json.dumps({})

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("El body es requerido para la petici\\u00f3n.", response['body'])

    @patch('teams.findByUser.app.get_team_from_user')
    @patch('teams.findByUser.app.get_user')
    @patch('teams.findByUser.app.validate_user_role')
    @patch('teams.findByUser.app.validate_token')
    def test_missing_useruid(self, mock_validate_token, mock_validate_user_role, mock_get_user, mock_get_team_from_user):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {"userUid": "user123"}
        mock_get_team_from_user.return_value = {"teamId": "equipo123", "teamName": "Equipo de Chombo"}

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("El campo userUid es requerido.", response['body'])

    @patch('teams.findByUser.app.validate_token')
    @patch('teams.findByUser.app.validate_user_role')
    @patch('teams.findByUser.app.get_user')
    def test_user_not_found(self, mock_get_user, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = None

        event = {
            "body": json.dumps({"userUid": "user123"})
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn("No existe ningun usuario con ese uid", response['body'])

    @patch('teams.findByUser.app.validate_token')
    @patch('teams.findByUser.app.validate_user_role')
    @patch('teams.findByUser.app.get_user')
    def test_client_error(self, mock_get_user, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.side_effect = ClientError({"Error": {"Code": "400"}}, "get_user")

        event = {
            "body": json.dumps({"userUid": "user123"})
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexi\\u00f3n. An error occurred (400) when calling the get_user operation: Unknown", response['body'])

    @patch('teams.findByUser.app.validate_token')
    @patch('teams.findByUser.app.validate_user_role')
    @patch('teams.findByUser.app.get_user')
    def test_unhandled_exception(self, mock_get_user, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.side_effect = Exception("Unhandled exception")

        event = {
            "body": json.dumps({"userUid": "user123"})
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Error de servidor", response['body'])


if __name__ == '__main__':
    unittest.main()
