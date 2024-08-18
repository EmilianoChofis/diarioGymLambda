import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.findById.app  import lambda_handler

class TestGetTeamById(unittest.TestCase):

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_get_team_by_id_success(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        #test sin errores
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231", "name": "Equipo 1231"}

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"id": "equipo1231"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Equipo encontrado", json.loads(result['body'])['message'])
        self.assertEqual(json.loads(result['body'])['data']['name'], "Equipo 1231")

    @patch('teams.findById.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #test token invalido
        mock_validate_token.return_value = (None, "Token inválido")

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"id": "equipo1231"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 401)
        self.assertIn("Token inválido", json.loads(result['body'])['message'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    def test_user_without_permissions(self, mock_validate_user_role, mock_validate_token):
        #test role sin permisos
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"id": "equipo1231"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 403)
        self.assertIn("No tienes permisos para realizar esta acción.", json.loads(result['body'])['message'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    def test_missing_body(self, mock_validate_user_role, mock_validate_token):
        #test sin body
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 400)
        self.assertIn("El body es requerido para la petición.", json.loads(result['body'])['message'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    def test_missing_id(self, mock_validate_user_role, mock_validate_token):
        #test el body tiene parametros incorrectos
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"name": "equipo josa"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 400)
        self.assertIn("El campo id es requerido.", json.loads(result['body'])['message'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_team_not_found(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        # test que no se encuentra el equipo con el equipo con el id
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.return_value = None

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"id": "equipoinexistente"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 404)
        self.assertIn("No existe ningun equipo con ese id", json.loads(result['body'])['message'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_client_error(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        #test disparar client error
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.side_effect = ClientError({"Error": {"Code": "ClientError"}}, "get_team_by_id")

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"id": "equipo1231"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(result['body'])['message'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_server_error(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        #test error inesperado
        mock_validate_token.return_value = ({"sub": "123456"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.side_effect = Exception("Error inesperado")

        event = {
            "headers": {
                "Authorization": "Bearer valid_token"
            },
            "body": json.dumps({"id": "equipo1231"})
        }

        result = lambda_handler(event, None)

        self.assertEqual(result['statusCode'], 500)
        self.assertIn("Error de servidor.", json.loads(result['body'])['message'])

if __name__ == '__main__':
    unittest.main()
