import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from users.getUserById.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('users.getUserById.app.connect_to_db')
    def test_successful(self, mock_connect_to_db):
        #test todo correcto
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value.fetchone.return_value = {
            'username': 'Joksan Bahena',
            'email': 'Coquito@utez.com',
            'role_id': 1,
            'enable': True
        }

        event = {
            'body': json.dumps({'id': 1})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], "Usuario encontrado")


    @patch('users.getUserById.app.connect_to_db')
    def test_missing_body(self, mock_connect_to_db):
        event = {
            'body': None
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('users.getUserById.app.connect_to_db')
    def test_missing_user_id(self, mock_connect_to_db):
        mock_connect_to_db.return_value = MagicMock()
        event = {
            'body': json.dumps({})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El campo id es requerido.")

    @patch('users.getUserById.app.connect_to_db')
    def test_invalid_user_id(self, mock_connect_to_db):
        mock_connect_to_db.return_value = MagicMock()
        event = {
            'body': json.dumps({'id': 'invalid'})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El campo id debe ser un número.")

    @patch('users.getUserById.app.connect_to_db')
    def test_db_connection_failure(self, mock_connect_to_db):
        mock_connect_to_db.return_value = None
        event = {
            'body': json.dumps({'id': 1})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde.")

    @patch('users.getUserById.app.connect_to_db')
    def test_user_not_found(self, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value.fetchone.return_value = None

        event = {
            'body': json.dumps({'id': 1})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "Usuario no encontrado.")


    @patch('users.getUserById.app.connect_to_db')
    def test_client_error(self, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.side_effect = ClientError(
            {"Error": {"Code": "ClientError", "Message": "Error de cliente"}},
            "test"
        )

        event = {
            'body': json.dumps({'id': 1})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexión", json.loads(response['body'])['message'])

    @patch('users.getUserById.app.connect_to_db')
    def test_generic_exception(self, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.side_effect = Exception("Error generico")

        event = {
            'body': json.dumps({'id': 1})
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Error de servidor", json.loads(response['body'])['message'])


if __name__ == '__main__':
    unittest.main()
