import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
#se deberia llamar lambda_handler pero ya que asi lo hizo el puc
from teams.findByCouchId.app import lamda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    @patch('teams.findByCouchId.app.get_team_by_couch_id')
    def test_successful_team_retrieval(self, mock_get_team_by_couch_id, mock_validate_user_role, mock_validate_token):
        # Test correcto, equipo encontrado
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_id.return_value = {"team_id": "equipo123"}

        event = {
            "body": json.dumps({"couch_id": "entrenadorchombo123"})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["message"], "Equipo encontrado")
        self.assertIn("data", body)
        self.assertEqual(body["data"]["team_id"], "equipo123")

    @patch('teams.findByCouchId.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        # Test token invalido
        mock_validate_token.return_value = (None, "Invalid token")

        event = {
            "body": json.dumps({"couch_id": "entrenadorchombo123"})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 401)
        self.assertEqual(body["message"], "Invalid token")

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    def test_insufficient_permissions(self, mock_validate_user_role, mock_validate_token):
        # Test no es couach
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({"couch_id": "entrenadorchombo123"})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 403)
        self.assertEqual(body["message"], "No tienes permisos para realizar esta acción.")

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    @patch('teams.findByCouchId.app.get_team_by_couch_id')
    def test_missing_body(self, mock_get_team_by_couch_id, mock_validate_user_role, mock_validate_token):
        # Test sin body en la petición
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_id.return_value = {"team_id": "equipo123"}

        event = json.dumps({})

        response = lamda_handler(event, None)
        body = json.loads(response["body"])
        print(response)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "El body es requerido para la petición.")

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    def test_missing_couch_id(self, mock_validate_user_role, mock_validate_token):
        # Test sin couch_id en el body
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True

        event = {
            "body": json.dumps({})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "El campo 'couch_id' es requerido para la petición.")

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    @patch('teams.findByCouchId.app.get_team_by_couch_id')
    def test_team_not_found(self, mock_get_team_by_couch_id, mock_validate_user_role, mock_validate_token):
        # Test equipo no encontrado
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_id.return_value = None

        event = {
            "body": json.dumps({"couch_id": "entrenadorchombo123"})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["message"], "No se encontró el equipo.")

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    @patch('teams.findByCouchId.app.get_team_by_couch_id')
    def test_client_error(self, mock_get_team_by_couch_id, mock_validate_user_role, mock_validate_token):
        # Test disparar un ClientError
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_id.side_effect = ClientError({"Error": {"Code": "500"}}, "SomeOperation")

        event = {
            "body": json.dumps({"couch_id": "entrenadorchombo123"})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Error en la conexión.", body["message"])

    @patch('teams.findByCouchId.app.validate_token')
    @patch('teams.findByCouchId.app.validate_user_role')
    @patch('teams.findByCouchId.app.get_team_by_couch_id')
    def test_exception(self, mock_get_team_by_couch_id, mock_validate_user_role, mock_validate_token):
        # Test disparar una excepción general
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_team_by_couch_id.side_effect = Exception("Excepción inesperada")

        event = {
            "body": json.dumps({"couch_id": "entrenadorchombo123"})
        }

        response = lamda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Error inesperado.", body["message"])


if __name__ == '__main__':
    unittest.main()
