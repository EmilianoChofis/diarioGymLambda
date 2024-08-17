import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from teams.accept_users.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    @patch('teams.accept_users.app.user_has_team')
    @patch('teams.accept_users.app.number_of_members')
    @patch('teams.accept_users.app.insert_user_group')
    def test_successful_registration(self, mock_insert_user_group, mock_number_of_members, mock_user_has_team, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        #test todo correcto
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = False
        mock_number_of_members.return_value = ["user1", "coquito"]
        mock_insert_user_group.return_value = True

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertIn('Usuario agregado al equipo correctamente.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    def test_invalid_token(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = (None, "Token inválido")
        #test token invalido
        event = {"body": json.dumps({})}

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertIn('Token inválido', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    def test_missing_role_permission(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = False
        #test sin permisso
        event = {"body": json.dumps({})}

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertIn('No tienes permisos para realizar esta acción.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    def test_missing_body(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        #test sin body otra vez, la clasica, la de siempre, la prueba que tengo que repetir una y otra vez
        #hola coquito
        event = {"body": json.dumps({})}

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('El body es requerido para la petición.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    def test_user_not_found(self, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        #test usuario inexistente
        mock_user_exists_in_db.return_value = False
        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn('No se encontró ningun usuario con ese uid.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    @patch('teams.accept_users.app.user_has_team')
    def test_user_already_has_team(self, mock_user_has_team, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        #test de usuario que ya cuenta con equipo
        mock_user_has_team.return_value = True

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertIn('El usuario ya tiene un equipo asignado.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    @patch('teams.accept_users.app.user_has_team')
    @patch('teams.accept_users.app.number_of_members')
    def test_team_full(self, mock_number_of_members, mock_user_has_team, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = False
        #xd ni siquiera recuerdo el formato en el que se regresan los users
        #hola coquito
        mock_number_of_members.return_value = ["user1", "user2", "user3", "user4", "user5","user6","user7","userOCHO"]

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 409)
        self.assertIn('El equipo ya tiene el número máximo de integrantes.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    @patch('teams.accept_users.app.user_has_team')
    @patch('teams.accept_users.app.number_of_members')
    @patch('teams.accept_users.app.insert_user_group')
    def test_insert_user_group_failure(self, mock_insert_user_group, mock_number_of_members, mock_user_has_team, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = False
        mock_number_of_members.return_value = ["user1", "user2"]
        #error al insetar el user
        mock_insert_user_group.return_value = None

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('No se pudo agregar el usuario al equipo.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    @patch('teams.accept_users.app.user_has_team')
    @patch('teams.accept_users.app.number_of_members')
    @patch('teams.accept_users.app.insert_user_group')
    def test_client_error(self, mock_insert_user_group, mock_number_of_members, mock_user_has_team, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.side_effect = ClientError({"Error": {"Code": "500", "Message": "Client error"}}, "operation_name")
        #client error, lo disparamos
        #sip otra vez este test
        #y no, no agrego comentarios
        #innecesarios para sumar mas
        #lineas de codigo en github
        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error en la conexión.', json.loads(response['body'])['message'])

    @patch('teams.accept_users.app.validate_token')
    @patch('teams.accept_users.app.validate_user_role')
    @patch('teams.accept_users.app.user_exists_in_db')
    @patch('teams.accept_users.app.get_team_by_id')
    @patch('teams.accept_users.app.user_has_team')
    @patch('teams.accept_users.app.number_of_members')
    @patch('teams.accept_users.app.insert_user_group')
    def test_server_error(self, mock_insert_user_group, mock_number_of_members, mock_user_has_team, mock_get_team_by_id, mock_user_exists_in_db, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "12345"}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_get_team_by_id.return_value = {"id": "equipo1231"}
        mock_user_has_team.return_value = False
        mock_number_of_members.return_value = ["user1", "user2"]
        #disparamos una excepcion pa que truene
        mock_insert_user_group.side_effect = Exception("Unknown error")

        event = {
            "body": json.dumps({
                "team": {"id": "equipo1231"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error de servidor.', json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()
