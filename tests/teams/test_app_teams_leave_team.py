import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.leave_team.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.user_has_team')
    @patch('teams.leave_team.app.remove_user_team')
    def test_successful_user_removal(self, mock_remove_user_team, mock_user_has_team, mock_get_team_by_id,mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        #test todo correcto
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], "Usuario eliminado del equipo correctamente.")

    @patch('teams.leave_team.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #test token invalido
        mock_validate_token.return_value = (None, "Token inválido")

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "Token inválido")

    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_bad_role(self, mock_validate_user_role, mock_validate_token):
        #test role invalido
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.user_has_team')
    @patch('teams.leave_team.app.remove_user_team')
    def test_missing_body(self, mock_remove_user_team, mock_user_has_team, mock_get_team_by_id,mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #test body invalido
        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.user_has_team')
    @patch('teams.leave_team.app.remove_user_team')
    def test_missing_team_field(self, mock_remove_user_team, mock_user_has_team, mock_get_team_by_id,mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #test sin equipo en body
        event = {
            "body": json.dumps({
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El campo team es requerido.")

    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.user_has_team')
    @patch('teams.leave_team.app.remove_user_team')
    def test_missing_user_field(self, mock_remove_user_team, mock_user_has_team, mock_get_team_by_id,mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #el mismo test de arriba pero ahora sin user pq da un mensaje distinto
        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "EL campo user es requerido.")

    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_user_not_found(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        #test usuario no encontrado
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = False

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")

    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_team_not_found(self, mock_validate_user_role, mock_validate_token, mock_get_team_by_id):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        #test equipo no encontrado
        mock_get_team_by_id.return_value = None

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun equipo con ese id.")

    @patch('teams.leave_team.app.user_has_team')
    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_user_not_in_team(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db, mock_get_team_by_id, mock_user_has_team):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        #test el usuario no esta con ese equipo
        mock_user_has_team.return_value = False

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "El usuario no pertenece a ese equipo.")

    @patch('teams.leave_team.app.remove_user_team')
    @patch('teams.leave_team.app.user_has_team')
    @patch('teams.leave_team.app.get_team_by_id')
    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_user_removal_failed(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db, mock_get_team_by_id, mock_user_has_team, mock_remove_user_team):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = True
        #test no se pudo borrar al usuario del equipo
        mock_remove_user_team.return_value = None

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "No se pudo eliminar al usuario del equipo.")

    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_client_error(self, mock_validate_user_role, mock_validate_token, user_exists_in_db):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        user_exists_in_db.side_effect = ClientError({"Error": {"Code": "ClientError"}}, "get_team_by_id")

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(response['body'])['message'])

    @patch('teams.leave_team.app.user_exists_in_db')
    @patch('teams.leave_team.app.validate_token')
    @patch('teams.leave_team.app.validate_user_role')
    def test_unhandled_exception(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db):
        mock_validate_token.return_value = ({"sub": "coquito1231"}, None)
        mock_validate_user_role.return_value = True
        #test disparamos un error caulquiera
        mock_user_exists_in_db.side_effect = Exception("Error inesperado")

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito1231"}
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Error de servidor.", json.loads(response['body'])['message'])


if __name__ == '__main__':
    unittest.main()
