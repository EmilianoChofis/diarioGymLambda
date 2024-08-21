import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from auth.register import app

class TestUserRegistrationLambdaHandler(unittest.TestCase):

    @patch('auth.register.app.insert_user_pool')
    @patch('auth.register.app.insert_user_db')
    @patch('auth.register.app.get_user_id_by_username')
    @patch('auth.register.app.email_exists_in_cognito')
    @patch('auth.register.app.user_exists_in_cognito')
    def test_successful_registration(self, mock_user_exists, mock_email_exists, mock_get_user_id, mock_insert_user_db, mock_insert_user_pool):
        # test prueba correctamente
        mock_user_exists.return_value = False
        mock_email_exists.return_value = False
        mock_get_user_id.return_value = "test_uid"

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test",
                "lastname": "User",
                "age": 30,
                "gender": "male"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], "Usuario registrado correctamente.")

    @patch('auth.register.app.user_exists_in_cognito')
    def test_user_already_exists(self, mock_user_exists):
        # test simulando usuario existente
        mock_user_exists.return_value = True

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test",
                "lastname": "User",
                "age": 30,
                "gender": "male"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "El usuario ya se encuentra registrado.")

    @patch('auth.register.app.user_exists_in_cognito')
    @patch('auth.register.app.email_exists_in_cognito')
    def test_email_already_exists(self, email_exists_in_cognito,mock_user_exists):
        # test correo ya ocupado
        mock_user_exists.return_value = False
        email_exists_in_cognito.return_value = True

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test",
                "lastname": "User",
                "age": 30,
                "gender": "male",
            })
        }

        response = app.lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "El correo ya se encuentra registrado.")
    @patch('auth.register.app.insert_user_pool')
    @patch('auth.register.app.user_exists_in_cognito')
    @patch('auth.register.app.email_exists_in_cognito')
    @patch('auth.register.app.get_user_id_by_username')
    def test_resource_not_found(self, get_user_id_by_username,email_exists_in_cognito,mock_user_exists,mock_insert_user_pool):
        # similacion recurso no encontrado
        mock_user_exists.return_value = False
        email_exists_in_cognito.return_value = False
        mock_insert_user_pool.return_valie ={
            'statusCode': 200,
            'body': json.dumps({"message": "User created successfully, verification email sent."})
        }
        get_user_id_by_username.side_effect = app.ResourceNotFound("error inesperado.")

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test",
                "lastname": "User",
                "age": 30,
                "gender": "male"
            })
        }

        response = app.lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "Recurso no encontrado. error inesperado.")

    @patch('auth.register.app.insert_user_pool')
    @patch('auth.register.app.user_exists_in_cognito')
    @patch('auth.register.app.email_exists_in_cognito')
    @patch('auth.register.app.get_user_id_by_username')
    def test_client_error(self, get_user_id_by_username,email_exists_in_cognito,mock_user_exists,mock_insert_user_pool):
        # test clientError
        mock_user_exists.return_value = False
        email_exists_in_cognito.return_value = False
        mock_insert_user_pool.return_valie ={
            'statusCode': 200,
            'body': json.dumps({"message": "User created successfully, verification email sent."})
        }
        get_user_id_by_username.side_effect = ClientError(
            {"Error": {"Code": "InvalidParameterException", "Message": "Error en la conexión."}},
            "AdminGetUser"
        )

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test",
                "lastname": "User",
                "age": 30,
                "gender": "male"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error en la conexión. An error occurred (InvalidParameterException) when calling the AdminGetUser operation: Error en la conexión.")

    def test_missing_parameters(self):
        # Test con parametros faltantes
        event = {"body": json.dumps({"email": "test@example.com",
                                     "username": "testuser"})}

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Faltan campos requeridos.")

    def test_missing_body(self):
        # Test sin body
        event = {"body":json.dumps({})}

        response = app.lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

if __name__ == '__main__':
    unittest.main()
