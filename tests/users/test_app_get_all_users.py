import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from users.getAllUsers.app import lambda_handler  # Ajusta esta importación según tu estructura de proyecto

class TestLambdaHandler(unittest.TestCase):


    @patch('users.getAllUsers.app.jwt.decode')
    @patch('users.getAllUsers.app.connect_to_db')
    def test_users_found(self, mock_connect_to_db, mock_jwt_decode):
        #test todo correcto
        mock_jwt_decode.return_value = {
            'cognito:groups': ['Admin']
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "coquito"}]
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        event = {
            "headers": {
                "Authorization": "Bearer TokenValido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Lista de usuarios obtenidos")
        self.assertEqual(len(json.loads(response['body'])['data']), 1)


    def test_missing_headers(self):
        #test sin headers
        event = {
            "headers": None
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    def test_missing_authorization(self):
        #test con headers pero sin token
        event = {
            "headers": {
                "Authorization": None
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    def test_invalid_authorization_format(self):
        #test con token invalido
        event = {
            "headers": {
                "Authorization": "TokenInvalido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('users.getAllUsers.app.jwt.decode')
    def test_no_admin(self, mock_jwt_decode):
        #usuario sin rol de admin
        mock_jwt_decode.return_value = {
            'cognito:groups': ['User']
        }

        event = {
            "headers": {
                "Authorization": "Bearer TokenValido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('users.getAllUsers.app.jwt.decode')
    @patch('users.getAllUsers.app.connect_to_db')
    def test_db_connection_failure(self, mock_connect_to_db, mock_jwt_decode):
        #usuario con rol de Admin
        mock_jwt_decode.return_value = {
            'cognito:groups': ['Admin']
        }
        #simula fallo en la conexion a la base de datos
        mock_connect_to_db.return_value = None

        event = {
            "headers": {
                "Authorization": "Bearer TokenValido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde.")

    @patch('users.getAllUsers.app.jwt.decode')
    @patch('users.getAllUsers.app.connect_to_db')
    def test_no_users_found(self, mock_connect_to_db, mock_jwt_decode):
        #usuario con rol de Admin
        mock_jwt_decode.return_value = {
            'cognito:groups': ['Admin']
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        # No se encuentran usuarios
        mock_cursor.fetchall.return_value = []
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        event = {
            "headers": {
                "Authorization": "Bearer TokenValido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], 'No se encontraron usuarios')


    @patch('users.getAllUsers.app.jwt.decode')
    @patch('users.getAllUsers.app.connect_to_db')
    def test_client_error(self, mock_connect_to_db, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            'cognito:groups': ['Admin'] 
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = ClientError({"Error": {"Code": "SomeError"}}, "Operation")

        event = {
            "headers": {
                "Authorization": "Bearer TokenValido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(response['body'])['message'])

    @patch('users.getAllUsers.app.jwt.decode')
    @patch('users.getAllUsers.app.connect_to_db')
    def test_generic_exception(self, mock_connect_to_db, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            'cognito:groups': ['Admin']
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Error Generico")

        event = {
            "headers": {
                "Authorization": "Bearer TokenValido"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Error Generico")

if __name__ == '__main__':
    unittest.main()
