import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from users.registerUser.app import lambda_handler, ResourceNotFound


class TestLambdaHandler(unittest.TestCase):

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    @patch('users.registerUser.app.user_exists_in_cognito')
    @patch('users.registerUser.app.email_exists_in_cognito')
    @patch('users.registerUser.app.insert_user_pool')
    @patch('users.registerUser.app.get_user_id_by_username')
    @patch('users.registerUser.app.insert_user_db')
    def test_successful_registration(self, mock_insert_user_db, mock_get_user_id_by_username, mock_insert_user_pool,mock_email_exists_in_cognito, mock_user_exists_in_cognito,mock_validate_user_role, mock_validate_token):
        #test todo correcto
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_cognito.return_value = False
        mock_email_exists_in_cognito.return_value = False
        mock_get_user_id_by_username.return_value = "test-user-id"

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",
                "lastname": "Rosales",
                "age": 22,
                "gender": "Masculino",
                "role": "User"
            })
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 201)
        self.assertIn("Usuario registrado correctamente.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    def test_missing_token(self, mock_validate_token):
        mock_validate_token.return_value = (None, "Token Invalido")

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 401)
        self.assertIn("Token Invalido", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    def test_unauthorized_role(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({}, None)
        #test rol imvlido
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 403)
        self.assertIn("No tienes permisos para realizar esta acción.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    def test_missing_fields(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",})
        }

        response = lambda_handler(event, {})
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Faltan campos requeridos.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    @patch('users.registerUser.app.user_exists_in_cognito')
    def test_user_already_exists(self, mock_user_exists_in_cognito, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_cognito.return_value = True

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",
                "lastname": "Rosales",
                "age": 22,
                "gender": "Masculino",
                "role": "User"
            })
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 409)
        self.assertIn("El usuario ya se encuentra registrado.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    @patch('users.registerUser.app.email_exists_in_cognito')
    def test_email_already_exists(self, mock_email_exists_in_cognito, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True
        mock_email_exists_in_cognito.return_value = True

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",
                "lastname": "Rosales",
                "age": 22,
                "gender": "Masculino",
                "role": "User"
            })
        }

        response = lambda_handler(event, {})
        self.assertEqual(response['statusCode'], 409)
        self.assertIn("El correo ya se encuentra registrado.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    def test_invalid_role(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test",
                "lastname": "User",
                "age": 25,
                "gender": "M",
                "role": "InvalidRole"
            })
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("El rol no es válido.", json.loads(response['body'])['message'])


    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    @patch('users.registerUser.app.user_exists_in_cognito')
    @patch('users.registerUser.app.email_exists_in_cognito')
    @patch('users.registerUser.app.insert_user_pool')
    @patch('users.registerUser.app.get_user_id_by_username')
    @patch('users.registerUser.app.insert_user_db')
    def test_user_not_found_in_cognito(self, mock_insert_user_db, mock_get_user_id_by_username, mock_insert_user_pool,mock_email_exists_in_cognito, mock_user_exists_in_cognito,mock_validate_user_role, mock_validate_token):
        #test user not found
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_cognito.return_value = False
        mock_email_exists_in_cognito.return_value = False
        mock_get_user_id_by_username.side_effect = ResourceNotFound("No se encontró el usuario.")

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",
                "lastname": "Rosales",
                "age": 22,
                "gender": "Masculino",
                "role": "User"
            })
        }

        response = lambda_handler(event, {})
        print(response)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn("No se encontró el usuario.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    @patch('users.registerUser.app.user_exists_in_cognito')
    @patch('users.registerUser.app.email_exists_in_cognito')
    @patch('users.registerUser.app.insert_user_pool')
    @patch('users.registerUser.app.get_user_id_by_username')
    @patch('users.registerUser.app.insert_user_db')
    def test_cognito_client_error(self, mock_insert_user_db, mock_get_user_id_by_username, mock_insert_user_pool,mock_email_exists_in_cognito, mock_user_exists_in_cognito,mock_validate_user_role, mock_validate_token):
        #test user not found
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_cognito.return_value = False
        mock_email_exists_in_cognito.return_value = False
        mock_get_user_id_by_username.side_effect = ClientError(
            {'Error': {'Message': 'Test error'}},
            'TestOperation'
        )

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",
                "lastname": "Rosales",
                "age": 22,
                "gender": "Masculino",
                "role": "User"
            })
        }

        response = lambda_handler(event, {})
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(response['body'])['message'])

    @patch('users.registerUser.app.validate_token')
    @patch('users.registerUser.app.validate_user_role')
    @patch('users.registerUser.app.insert_user_pool')
    def test_server_error(self,mock_insert_user_pool, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({}, None)
        mock_validate_user_role.return_value = True
        mock_insert_user_pool.side_effect=Exception("Error generico")

        event = {
            "body": json.dumps({
                "email": "jdrj40@gmail.com",
                "username": "Jonathan Doe",
                "name": "David",
                "lastname": "Rosales",
                "age": 22,
                "gender": "Masculino",
                "role": "User"
            })
        }

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Error de servidor.", json.loads(response['body'])['message'])


if __name__ == '__main__':
    unittest.main()
