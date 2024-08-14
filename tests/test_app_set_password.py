import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from auth.set_password import app  # Asegúrate de ajustar la ruta según tu estructura de proyecto

class TestChangePasswordLambdaHandler(unittest.TestCase):

    @patch('auth.set_password.app.user_exists_in_cognito')
    @patch('auth.set_password.app.boto3.client')
    def test_successful_password_change(self, mock_boto_client, mock_user_exists):
        # Simulamos que el usuario existe
        mock_user_exists.return_value = True

        # simulacion del boto3 client
        mock_client_instance = MagicMock()
        mock_client_instance.admin_initiate_auth.return_value = {
            'ChallengeName': 'NEW_PASSWORD_REQUIRED',
            'Session': 'test_session'
        }
        mock_boto_client.return_value = mock_client_instance

        event = {
            "body": json.dumps({
                "username": "josafat",
                "temporary_password": "abc123",
                "new_password": "abc1234"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Cambio de contraseña correcto.")

    @patch('auth.set_password.app.user_exists_in_cognito')
    @patch('auth.set_password.app.boto3.client')
    def test_user_not_exist(self, mock_boto_client, mock_user_exists):
        # simulacion un usuario inexistente
        mock_user_exists.return_value = False

        event = {
            "body": json.dumps({
                "username": "Josafat",
                "temporary_password": "abc123",
                "new_password": "abc1234"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error_message'], "El usaurio no existe.")

    @patch('auth.set_password.app.user_exists_in_cognito')
    @patch('auth.set_password.app.boto3.client')
    def test_client_error(self, mock_boto_client, mock_user_exists):
        # usuario existente
        mock_user_exists.return_value = True

        # simulacon de un ClientError
        mock_client_instance = MagicMock()
        mock_client_instance.admin_initiate_auth.side_effect = ClientError(
            {"Error": {"Code": "InvalidParameterException", "Message": "Error no he dormido en 3 dias."}},
            "AdminInitiateAuth"
        )
        mock_boto_client.return_value = mock_client_instance

        event = {
            "body": json.dumps({
                "username": "JosafatAyudamePorfavor",
                "temporary_password": "abc123",
                "new_password": "abc1231"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error no he dormido en 3 dias.")

    def test_missing_parameters(self):
        # Test con parámetros faltantes
        event = {
            "body": json.dumps({
                "username": "JosafatTeOdio",
                "temporary_password": "Ni siquiera vas a leer esto"
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error_message'], "Campos faltantes.")

    def test_missing_body(self):
        # Test sin body
        event = {"body": json.dumps({})}

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error_message'], "Campos faltantes.")

if __name__ == '__main__':
    unittest.main()
