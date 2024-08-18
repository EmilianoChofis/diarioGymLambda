import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.findAll.app import lambda_handler

class TestGetTeams(unittest.TestCase):

    @patch('teams.findAll.app.validate_token')
    @patch('teams.findAll.app.validate_user_role')
    @patch('teams.findAll.app.get_teams')
    def test_get_teams_success(self, mock_get_teams, mock_validate_user_role, mock_validate_token):
        #simulacion correcta
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_teams.return_value = [
            {"id": "equipo1231", "name": "Equipo 1"},
            {"id": "equipo1232", "name": "Equipo 2"}
        ]

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Lista de equipos registrados.", json.loads(result['body'])['message'])
        self.assertEqual(len(json.loads(result['body'])['data']), 2)

    @patch('teams.findAll.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #test token invalido
        mock_validate_token.return_value = (None, "Token inválido")

        event = {
            "headers": {
                "Authorization": "Bearer invalid_token"
            },
            "body": json.dumps({})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 401)
        self.assertIn("Token inválido", json.loads(result['body'])['message'])

    @patch('teams.findAll.app.validate_token')
    @patch('teams.findAll.app.validate_user_role')
    def test_user_without_permissions(self, mock_validate_user_role, mock_validate_token):
        #test sin permisos
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 403)
        self.assertIn("No tienes permisos para realizar esta acción.", json.loads(result['body'])['message'])

    @patch('teams.findAll.app.validate_token')
    @patch('teams.findAll.app.validate_user_role')
    @patch('teams.findAll.app.get_teams')
    def test_client_error(self, mock_get_teams, mock_validate_user_role, mock_validate_token):
        #test client error
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_teams.side_effect = ClientError({"Error": {"Code": "ClientError"}}, "get_teams")

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(result['body'])['message'])

    @patch('teams.findAll.app.validate_token')
    @patch('teams.findAll.app.validate_user_role')
    @patch('teams.findAll.app.get_teams')
    def test_server_error(self, mock_get_teams, mock_validate_user_role, mock_validate_token):
        #test disparar una excepcion cualquiera
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_teams.side_effect = Exception("Excepcion cualquiera")

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 500)
        self.assertIn("Error de servidor.", json.loads(result['body'])['message'])

if __name__ == '__main__':
    unittest.main()
