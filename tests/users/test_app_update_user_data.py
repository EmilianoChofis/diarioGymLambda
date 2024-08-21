import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from users.updateUserData.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.modify_user')
    def test_success(self, mock_modify_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        #test todo correcto
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {'id': 'usuario123'}
        mock_modify_user.return_value = True

        event = {
            "body": json.dumps({
                "id": "usuario123",
                "name": "David",
                "lastname": "Rosales",
                "age": 23,
                "gender": "Masculino"
            })
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Usuario actualizado correctamente.")

    @patch('users.updateUserData.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #token invalido
        mock_validate_token.return_value = (None, "Token invalido")

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "Token invalido")

    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    def test_unauthorized_role(self, mock_validate_user_role, mock_validate_token):
        #rol no autorizado
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.modify_user')
    def test_missing_body(self, mock_modify_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        #test sin body
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {'id': 'usuario123'}
        mock_modify_user.return_value = True
        event = json.dumps({})

        response = lambda_handler(event, {})

        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.modify_user')
    def test_missing_fields(self, mock_modify_user, mock_get_user, mock_validate_user_role, mock_validate_token):
        #test campos faltantes
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {'id': 'usuario123'}
        mock_modify_user.return_value = True
        event = {
            "body": json.dumps({
                "id": "usuario123",
                "name": "David",
                "lastname": "Rosales",
            })
        }

        response = lambda_handler(event, {})


        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Falatan campos requeridos.")

    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    def test_user_not_found(self, mock_validate_user_role, mock_validate_token, mock_get_user):
        #test usuario no encontrado
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = None

        event = {
            "body": json.dumps({
                "id": "usuario123",
                "name": "David",
                "lastname": "Rosales",
                "age": 23,
                "gender": "Masculino"
            })
        }

        response = lambda_handler(event, {})


        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")

    @patch('users.updateUserData.app.modify_user')
    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    def test_modify_user_error(self, mock_validate_user_role, mock_validate_token, mock_get_user, mock_modify_user):

        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {'id': 'usuario123'}
        mock_modify_user.return_value = False

        event = {
            "body": json.dumps({
                "id": "usuario123",
                "name": "David",
                "lastname": "Rosales",
                "age": 23,
                "gender": "Masculino"
            })
        }

        response = lambda_handler(event, {})


        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error al actualizar el usuario.")

    @patch('users.updateUserData.app.modify_user')
    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    def test_client_error(self, mock_validate_user_role, mock_validate_token, mock_get_user, mock_modify_user):
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {'id': 'usuario123'}
        mock_modify_user.side_effect = ClientError({"Error": {"Code": "400", "Message": "Client error"}}, "Error")

        event = {
            "body": json.dumps({
                "id": "usuario123",
                "name": "David",
                "lastname": "Rosales",
                "age": 23,
                "gender": "Masculino"
            })
        }

        response = lambda_handler(event, {})


        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(response['body'])['message'])

    @patch('users.updateUserData.app.modify_user')
    @patch('users.updateUserData.app.get_user')
    @patch('users.updateUserData.app.validate_token')
    @patch('users.updateUserData.app.validate_user_role')
    def test_generic_exception(self, mock_validate_user_role, mock_validate_token, mock_get_user, mock_modify_user):
        mock_validate_token.return_value = ({'sub': 'usuario123'}, None)
        mock_validate_user_role.return_value = True
        mock_get_user.return_value = {'id': 'usuario123'}
        mock_modify_user.side_effect = Exception("Excepcion generica")

        event = {
            "body": json.dumps({
                "id": "usuario123",
                "name": "David",
                "lastname": "Rosales",
                "age": 23,
                "gender": "Masculino"
            })
        }

        response = lambda_handler(event, {})


        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error interno del servidor.")


if __name__ == '__main__':
    unittest.main()
