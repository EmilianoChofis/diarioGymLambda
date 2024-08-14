import unittest
from unittest.mock import patch, MagicMock
import json

import jwt
import pymysql
from exercises.register.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('exercises.register.app.connect_to_db')
    @patch('exercises.register.app.jwt.decode')
    def test_successful_creation(self, mock_jwt_decode, mock_connect_to_db):
        #simulacionde un token válido y una conexión de base de datos exitosa
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.return_value = None
        mock_connection.commit.return_value = None

        event = {
            'body': json.dumps({
                'created_by': 'DavidRDJ',
                'name': 'Levantamiento de gluteos',
                'description': 'hola coquito'
            }),
            'headers': {
                'Authorization': 'Bearer josatoken'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], "Ejercicio creado exitosamente.")

    @patch('exercises.register.app.connect_to_db')
    @patch('exercises.register.app.jwt.decode')
    def test_missing_authorization_header(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connect_to_db.return_value = MagicMock()
        #no enviamos el token
        event = {
            'body': json.dumps({
                'created_by': 'DavidRDJ',
                'name': 'Levantamiento de gluteos',
                'description': 'hola coquito'
            }),
            'headers': None
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('exercises.register.app.connect_to_db')
    @patch('exercises.register.app.jwt.decode')
    def test_invalid_token(self, mock_jwt_decode, mock_connect_to_db):
        #excepcion de jwt
        mock_jwt_decode.side_effect = jwt.DecodeError
        mock_connect_to_db.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'created_by': 'DavidRDJ',
                'name': 'Levantamiento de gluteos',
                'description': 'hola coquito'
            }),
            'headers': {
                'Authorization': 'Bearer tokenInvalido'
            }
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Vuelve a intentarlo más tarde.")

    @patch('exercises.register.app.connect_to_db')
    @patch('exercises.register.app.jwt.decode')
    def test_missing_body(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connect_to_db.return_value = MagicMock()

        event = {
            'body': None,
            'headers': {
                'Authorization': 'Bearer oye.Josa.CTM'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('exercises.register.app.connect_to_db')
    @patch('exercises.register.app.jwt.decode')
    def test_missing_parameters(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connect_to_db.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'created_by': 'DavidRDJ'
                # qitamos nombre y descriptcion
            }),
            'headers': {
                'Authorization': 'Bearer oye.Josa.CTM'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Los campos created_by, name y description son requeridos.")


    @patch('exercises.register.app.connect_to_db')
    @patch('exercises.register.app.jwt.decode')
    def test_mysql_error(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = pymysql.MySQLError("MySQL error")

        event = {
            'body': json.dumps({
                'created_by': 'DavidRDJ',
                'name': 'Levantamiento de gluteos',
                'description': 'hola coquito'
            }),
            'headers': {
                'Authorization': 'Bearer tokenInvalido'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Vuelve a intentarlo más tarde.")

if __name__ == '__main__':
    unittest.main()
