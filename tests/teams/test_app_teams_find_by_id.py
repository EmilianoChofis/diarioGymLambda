import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.findById.app  import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    @patch('teams.findById.app.get_users_from_team')
    @patch('teams.findById.app.get_couch_by_uid')
    def test_successful_team(self, mock_get_couch_by_uid, mock_get_users_from_team, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        #todo correcto
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo123", "couch_id": "couchombo123"}
        mock_get_users_from_team.return_value = [{"id": "furcio"}, {"id": "woody"}]
        mock_get_couch_by_uid.return_value = {"id": "couchombo123", "name": "chombo hernandez"}

        event = {
            "body": json.dumps({"id": "equipo123"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn("Equipo encontrado", response['body'])
        self.assertIn("equipo123", response['body'])
        self.assertIn("furcio", response['body'])
        self.assertIn("chombo hernandez", response['body'])

    @patch('teams.findById.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        mock_validate_token.return_value = (None, "Token invalido")

        event = {
            "body": json.dumps({"id": "equipo123"})
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 401)
        self.assertIn("Token invalido", response['body'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    def test_unauthorized_user(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({"id": "equipo123"})
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 403)
        #perdon el acento daba un error asi que asi se queda
        self.assertIn("No tienes permisos para realizar esta acci\\u00f3n.", response['body'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    @patch('teams.findById.app.get_users_from_team')
    @patch('teams.findById.app.get_couch_by_uid')
    def test_missing_body(self, mock_get_couch_by_uid, mock_get_users_from_team, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        #test sin body
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo123", "couch_id": "couchombo123"}
        mock_get_users_from_team.return_value = [{"id": "furcio"}, {"id": "woody"}]
        mock_get_couch_by_uid.return_value = {"id": "couchombo123", "name": "chombo hernandez"}

        event = json.dumps({
        })

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        #mismo problema xd
        self.assertIn("El body es requerido para la petici\\u00f3n.", response['body'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    @patch('teams.findById.app.get_users_from_team')
    @patch('teams.findById.app.get_couch_by_uid')
    def test_missing_id(self, mock_get_couch_by_uid, mock_get_users_from_team, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        #test sin id
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo123", "couch_id": "couchombo123"}
        mock_get_users_from_team.return_value = [{"id": "furcio"}, {"id": "woody"}]
        mock_get_couch_by_uid.return_value = {"id": "couchombo123", "name": "chombo hernandez"}

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("El campo id es requerido", response['body'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_team_not_found(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.return_value = None

        event = {
            "body": json.dumps({"id": "equipo123"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn("No existe ningun equipo con ese id", response['body'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_client_error(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.side_effect = ClientError({"Error": {"Code": "400"}}, "get_team_by_id")

        event = {
            "body": json.dumps({"id": "equipo123"})
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        #aqui vamos de nuevo con el \\u00f3
        self.assertIn("Error en la conexi\\u00f3n. An error occurred (400) when calling the get_team_by_id operation: Unknown", response['body'])

    @patch('teams.findById.app.validate_token')
    @patch('teams.findById.app.validate_user_role')
    @patch('teams.findById.app.get_team_by_id')
    def test_unhandled_exception(self, mock_get_team_by_id, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito123"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_id.side_effect = Exception("Unhandled exception")

        event = {
            "body": json.dumps({"id": "equipo123"})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        #bueno este no tiene acentos
        self.assertIn("Error de servidor", response['body'])


if __name__ == '__main__':
    unittest.main()
