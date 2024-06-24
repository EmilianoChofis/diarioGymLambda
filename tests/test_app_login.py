import unittest
from unittest.mock import patch, MagicMock
import json

import pymysql

from auth.login import app


class TestLambdaHandler(unittest.TestCase):

    @patch('auth.login.db_conn.connect_to_db')
    def test_lambda_handler_no_body(self, mock_connect_to_db):
        event = {}
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('El body es requerido', response['body'])

    @patch('lambda_function.connect_to_db')
    def test_lambda_handler_missing_email_password(self, mock_connect_to_db):
        event = {
            'body': json.dumps({})
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Los campos email y password son requeridos', response['body'])

    @patch('lambda_function.connect_to_db')
    def test_lambda_handler_db_connection_fail(self, mock_connect_to_db):
        mock_connect_to_db.return_value = None
        event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'password': 'password123'
            })
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error de servidor. No se pudo conectar a la base de datos', response['body'])

    @patch('lambda_function.connect_to_db')
    def test_lambda_handler_success(self, mock_connect_to_db):
        # Mock the database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1, 'email': 'test@example.com'
        }

        event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'password': 'password123'
            })
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Login exitoso', response['body'])

    @patch('lambda_function.connect_to_db')
    def test_lambda_handler_invalid_credentials(self, mock_connect_to_db):
        # Mock the database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 401)
        self.assertIn('Credenciales inválidas', response['body'])

    @patch('lambda_function.connect_to_db')
    def test_lambda_handler_db_error(self, mock_connect_to_db):
        # Mock the database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = pymysql.MySQLError("DB Error")

        event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'password': 'password123'
            })
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error de servidor. Vuelve a intentarlo más tarde.', response['body'])
