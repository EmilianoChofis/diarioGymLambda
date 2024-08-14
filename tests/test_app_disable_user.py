import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from users.disableUser import app


class TestLambdaHandler(unittest.TestCase):

    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    @patch('users.disableUser.app.get_user')
    @patch('users.disableUser.app.change_status_user')
    def test_successful_status_change(self, mock_change_status_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        #Test que simula que el usuario es admin
        mock_validate_token.return_value = ({'user': 'admin'}, None)
        mock_validate_user_role.return_value = True
        # ahora un usuario activo que se cambiara a incativo
        mock_get_user.return_value = {'status': 'activo'}
        mock_change_status_user.return_value = True

        # Body con id del usuario
        event = {
            "body": json.dumps({"id": 1})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn("message", json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], "Status del usuario modificado exitosamente.")
        print(json.loads(response['body'])['message'])

    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    def test_invalid_token(self, mock_validate_user_role, mock_validate_token):
        # Simula que el token no es válido
        mock_validate_token.return_value = (None, "Token inválido")

        event = {
            "body": json.dumps({"id": 1})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertIn("message", json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], "Token inválido")
        print(json.loads(response['body'])['message'])

    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    def test_insufficient_permissions(self, mock_validate_user_role, mock_validate_token):
        # Test de usuario sin permisos osea no admin xd
        mock_validate_token.return_value = ({'user': 'user'}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({"id": 1})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertIn("message", json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")
        print(json.loads(response['body'])['message'])
    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    @patch('users.disableUser.app.get_user')
    def test_user_not_found(self, mock_get_user, mock_validate_user_role, mock_validate_token):
        # test token valido y admin pero no encontrara el usuaio
        mock_validate_token.return_value = ({'user': 'admin'}, None)
        mock_validate_user_role.return_value = True
        # simulamos que no retorna ningun usuario
        mock_get_user.return_value = None

        event = {
            "body": json.dumps({"id": 1})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn("message", json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")
        print(json.loads(response['body'])['message'])

    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    @patch('users.disableUser.app.get_user')
    @patch('users.disableUser.app.change_status_user')
    def test_change_status_user_failure(self, mock_change_status_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        # token valido y admin
        mock_validate_token.return_value = ({'user': 'admin'}, None)
        mock_validate_user_role.return_value = True
        # usuario activo
        mock_get_user.return_value = {'status': 'activo'}
        # pero forzamos un retorno falso simulando un error de la base de dato s
        mock_change_status_user.return_value = False

        event = {
            "body": json.dumps({"id": 1})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn("message", json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], "Error al modificar el status del usuario.")
        print(json.loads(response['body'])['message'])

    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    @patch('users.disableUser.app.get_user')
    @patch('users.disableUser.app.change_status_user')
    def test_missing_body(self, mock_change_status_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        # test para probar que valide que este el campo id en el body
        mock_validate_token.return_value = ({'user': 'admin'}, None)
        mock_validate_user_role.return_value = True

        event = {
            "body": json.dumps({"otroCampo":"Josafat"})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("message", json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], "El campo id es requerido.")
        print(json.loads(response['body'])['message'])

    @patch('users.disableUser.app.validate_token')
    @patch('users.disableUser.app.validate_user_role')
    @patch('users.disableUser.app.get_user')
    @patch('users.disableUser.app.change_status_user')
    def test_client_error(self, mock_change_status_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        # Simula el client error que dispara la excepcion
        mock_validate_token.side_effect = ClientError({"Error": {"Code": "Error", "Message": "Error"}}, "Operation")

        event = {
            "body": json.dumps({"id": 1})
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("message", json.loads(response['body']))
        self.assertIn("Error en la conexión", json.loads(response['body'])['message'])
        print(json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()
