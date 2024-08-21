import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from auth.login import app

class TestAuthLambdaHandler(unittest.TestCase):

    @patch('auth.login.app.boto3.client')
    def test_successful_authentication(self, mock_boto_client):
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        mock_cognito_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'IdToken': 'test_id_token',
                'AccessToken': 'test_access_token',
                'RefreshToken': 'test_refresh_token'
            }
        }
        #simulamos que esta en el gupo de Admin
        mock_cognito_client.admin_list_groups_for_user.return_value = {
            'Groups': [{'GroupName': 'Admin'}]
        }

        # simulamos el id y pool de cognito
        with patch.dict('os.environ', {'CLIENT_ID': 'test_client_id', 'POOL_ID': 'test_pool_id'}):
            event = {
                "body": json.dumps({"username": "testuser", "password": "testpassword"})
            }

            response = app.lambda_handler(event, None)

            self.assertEqual(response['statusCode'], 200)
            self.assertIn("id_token", json.loads(response['body']))
            self.assertIn("access_token", json.loads(response['body']))
            self.assertIn("refresh_token", json.loads(response['body']))
            self.assertEqual(json.loads(response['body'])['role'], "Admin")
    @patch('auth.login.app.boto3.client')
    def test_invalid_credentials(self, mock_boto_client):
        # simulamos un error por credenciales invalidas
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        mock_cognito_client.initiate_auth.side_effect = ClientError(
            {"Error": {"Code": "NotAuthorizedException", "Message": "El usuario o contraseña no son correctos, por favor denme chamba"}},
            "InitiateAuth"
        )

        with patch.dict('os.environ', {'CLIENT_ID': 'test_client_id', 'POOL_ID': 'test_pool_id'}):
            event = {
                "body": json.dumps({"username": "testuser", "password": "wrongpassword"})
            }

            response = app.lambda_handler(event, None)

            self.assertEqual(response['statusCode'], 400)
            self.assertIn("error_message", json.loads(response['body']))
            self.assertEqual(json.loads(response['body'])['error_message'], "El usuario o contraseña no son correctos, por favor denme chamba")

    @patch('auth.login.app.boto3.client')
    def test_internal_server_error(self, mock_boto_client):
        # Simulamos una excepcion, la que sea para que caiga en el catch final
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        mock_cognito_client.initiate_auth.side_effect = Exception("Error inesperado, tu lamda no funciona")

        with patch.dict('os.environ', {'CLIENT_ID': 'test_client_id', 'POOL_ID': 'test_pool_id'}):
            event = {
                "body": json.dumps({"username": "testuser", "password": "testpassword"})
            }

            response = app.lambda_handler(event, None)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn("error_message", json.loads(response['body']))
            self.assertEqual(json.loads(response['body'])['error_message'], "Error inesperado, tu lamda no funciona")

if __name__ == '__main__':
    unittest.main()
