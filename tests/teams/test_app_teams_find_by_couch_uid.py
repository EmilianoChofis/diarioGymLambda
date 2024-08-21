import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError

from teams.findByCouchUid.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    @patch('teams.findByCouchUid.app.get_team_by_couch_uid')
    @patch('teams.findByCouchUid.app.get_users_from_team')
    @patch('teams.findByCouchUid.app.get_couch_by_uid')
    def test_successful_team_retrieval(self, mock_get_couch_by_uid, mock_get_users_from_team, mock_get_team_by_couch_uid, mock_validate_user_role, mock_validate_token):
        # Test correcto, equipo encontrado
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_uid.return_value = {"id": "equipo123", "couch_id": "couchombo123"}
        mock_get_users_from_team.return_value = [{"user_id": "coquito1"}, {"user_id": "coquito2"}]
        mock_get_couch_by_uid.return_value = {"couch_id": "couchombo123"}

        event = {
            "body": json.dumps({"couchUid": "couchombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["message"], "Equipo encontrado")
        self.assertIn("data", body)
        self.assertEqual(body["data"]["id"], "equipo123")
        self.assertEqual(len(body["data"]["users"]), 2)
        self.assertIsNotNone(body["data"]["couch"])

    @patch('teams.findByCouchUid.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        # Test token inválido
        mock_validate_token.return_value = (None, "Invalid token")

        event = {
            "body": json.dumps({"couchUid": "couchombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 401)
        self.assertEqual(body["message"], "Invalid token")

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    def test_insufficient_permissions(self, mock_validate_user_role, mock_validate_token):
        # Test sin permisos
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({"couchUid": "couchombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 403)
        self.assertEqual(body["message"], "No tienes permisos para realizar esta acción.")

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    def test_missing_body(self, mock_validate_user_role, mock_validate_token):
        # Test sin body en la petición
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True

        event = json.dumps({})

        response = lambda_handler(event, None)
        body = json.loads(response["body"])
        print(response)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "El body es requerido para la petición.")

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    def test_missing_couch_uid(self, mock_validate_user_role, mock_validate_token):
        # Test sin couchUid en el body
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "El campo couchUid es requerido.")

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    @patch('teams.findByCouchUid.app.get_team_by_couch_uid')
    def test_team_not_found(self, mock_get_team_by_couch_uid, mock_validate_user_role, mock_validate_token):
        # Test equipo no encontrado
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_uid.return_value = None

        event = {
            "body": json.dumps({"couchUid": "couchombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["message"], "No existe ningun equipo con ese id")

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    @patch('teams.findByCouchUid.app.get_team_by_couch_uid')
    def test_client_error(self, mock_get_team_by_couch_uid, mock_validate_user_role, mock_validate_token):
        # Test disparar un ClientError
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_uid.side_effect = ClientError({"Error": {"Code": "500"}}, "SomeOperation")

        event = {
            "body": json.dumps({"couchUid": "couchombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Error en la conexión.", body["message"])

    @patch('teams.findByCouchUid.app.validate_token')
    @patch('teams.findByCouchUid.app.validate_user_role')
    @patch('teams.findByCouchUid.app.get_team_by_couch_uid')
    def test_exception(self, mock_get_team_by_couch_uid, mock_validate_user_role, mock_validate_token):
        # Test disparar una excepción general
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_uid.side_effect = Exception("Excepción inesperada")

        event = {
            "body": json.dumps({"couchUid": "couchombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Error de servidor.", body["message"])


if __name__ == '__main__':
    unittest.main()
