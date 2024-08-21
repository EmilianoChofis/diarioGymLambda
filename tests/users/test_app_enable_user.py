import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from users.enableUser.app import lambda_handler  # Asegúrate de ajustar esta importación según tu estructura de proyecto

class TestLambdaHandler(unittest.TestCase):

    @patch('users.enableUser.app.connect_to_db')
    def test_successful(self, mock_connect_to_db):
        #mock de la conexión a la base de datos
        #test todo correcto
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        event = {
            "body": json.dumps({
                "id": 1
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Usuario habilitado correctamente')

    def test_missing_body(self):
        #sin body
        event = {
            "body": None
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'El body es requerido para la petición.')

    def test_missing_id(self):
        #test sin el campo id
        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'El campo id es requerido.')

    def test_invalid_id_type(self):
        #test un string en el id
        event = {
            "body": json.dumps({
                "id": "holacoquito"
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'El campo id debe ser un número.')

    @patch('users.enableUser.app.connect_to_db')
    def test_db_connection_failure(self, mock_connect_to_db):
        #test sin conexion a base
        mock_connect_to_db.return_value = None

        event = {
            "body": json.dumps({
                "id": 1
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde.")

    @patch('users.enableUser.app.connect_to_db')
    def test_client_error(self, mock_connect_to_db):
        #disparamos el client error
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = ClientError({"Error": {"Code": "SomeError"}}, "Operation")

        event = {
            "body": json.dumps({
                "id": 1
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Error en la conexión.", json.loads(response['body'])['message'])

    @patch('users.enableUser.app.connect_to_db')
    def test_generic_exception(self, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Error Generico")

        event = {
            "body": json.dumps({
                "id": 1
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Vuelve a intentarlo más tarde.")

if __name__ == '__main__':
    unittest.main()
