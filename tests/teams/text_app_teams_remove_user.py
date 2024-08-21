import json
import unittest
from unittest.mock import patch, MagicMock

from botocore.exceptions import ClientError

from teams.remove_user.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_lambda_handler_successful_removal(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        #test todo correcto
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], "Usuario eliminado del equipo correctamente.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    def test_lambda_handler_invalid_token(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = (None, "Token inválido")

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "Token inválido")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    def test_lambda_handler_unauthorized_role(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_no_body(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        #test sin body
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True

        event = json.dumps({
        })

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_missing_field(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #test sin un campo requerido
        event = {
            "body": json.dumps({
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El campo couch es requerido.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_missing_value(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #test ahora con e campo requerido pero sin valor
        event = {
            "body": json.dumps({
                "couch": {},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "EL campo uid del couch es requerido.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_missing_user_field(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #test sin un campo requerido
        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "EL campo user es requerido.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_missing_user_value(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = True
        #test de nuevo con el campo user pero sin el valor
        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "EL campo user.uid es requerido.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_couch_no_team(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = None

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "El couch no cuenta con ningun equipo registrado.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_user_not_found(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = False

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_user_not_from_team(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = False

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "El usuario no pertenece al equipo del couch.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_user_not_from_team(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.return_value = None

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "No se pudo eliminar al usuario del equipo.")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_client_Error(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.side_effect = ClientError({"Error": {"Code": "error"}}, "erorr")

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error en la conexión. An error occurred (error) when calling the erorr operation: Unknown")

    @patch('teams.remove_user.app.validate_token')
    @patch('teams.remove_user.app.validate_user_role')
    @patch('teams.remove_user.app.get_couch_team')
    @patch('teams.remove_user.app.user_exists_in_db')
    @patch('teams.remove_user.app.user_has_team')
    @patch('teams.remove_user.app.remove_user_team')
    def test_generic_Error(self, mock_remove_user_team, mock_user_has_team, mock_user_exists_in_db, mock_get_couch_team, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "user"}, None)
        mock_validate_user_role.return_value = True
        mock_get_couch_team.return_value = {"id": "equipoChombo"}
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = True
        mock_remove_user_team.side_effect = Exception("Error generico")

        event = {
            "body": json.dumps({
                "couch": {"uid": "couchombo"},
                "user": {"uid": "coquito"}
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Error generico")

if __name__ == '__main__':
    unittest.main()