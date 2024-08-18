import unittest
from unittest.mock import patch, MagicMock
import json
import jwt
import pymysql
from exercises.update.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('exercises.update.app.connect_to_db')
    @patch('exercises.update.app.jwt.decode')
    def test_successful_update(self, mock_jwt_decode, mock_connect_to_db):
        # Simulación de un token válido y una conexión de base de datos exitosa
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.return_value = None
        mock_connection.commit.return_value = None

        event = {
            'body': json.dumps({
                'exercise_id': '1',
                'name': 'Levantamiento de gluteos',
                'description': 'Descripción actualizada'
            }),
            'headers': {
                'Authorization': 'Bearer validtoken'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Ejercicio actualizado exitosamente.")

    @patch('exercises.update.app.connect_to_db')
    @patch('exercises.update.app.jwt.decode')
    def test_missing_authorization_header(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connect_to_db.return_value = MagicMock()
    # test sin header
        event = {
            'body': json.dumps({
                'exercise_id': '1',
                'name': 'Levantamiento de gluteos',
                'description': 'Descripción actualizada'
            }),
            'headers': None
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('exercises.update.app.connect_to_db')
    @patch('exercises.update.app.jwt.decode')
    def test_invalid_token(self, mock_jwt_decode, mock_connect_to_db):
        # test de un token inválido
        mock_jwt_decode.side_effect = jwt.DecodeError
        mock_connect_to_db.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'exercise_id': '1',
                'name': 'Levantamiento de gluteos',
                'description': 'Descripción actualizada'
            }),
            'headers': {
                'Authorization': 'Bearer invalidtoken'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Vuelve a intentarlo más tarde.")

    @patch('exercises.update.app.connect_to_db')
    @patch('exercises.update.app.jwt.decode')
    def test_missing_body(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connect_to_db.return_value = MagicMock()
        #test sin body
        event = {
            'body': None,
            'headers': {
                'Authorization': 'Bearer validtoken'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    @patch('exercises.update.app.connect_to_db')
    @patch('exercises.update.app.jwt.decode')
    def test_missing_parameters(self, mock_jwt_decode, mock_connect_to_db):
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connect_to_db.return_value = MagicMock()
        #test sin parametros importantes
        event = {
            'body': json.dumps({
                'exercise_id': '1'
                # No se envían name y description
            }),
            'headers': {
                'Authorization': 'Bearer validtoken'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Los campos exercise_id, name y description son requeridos.")

    @patch('exercises.update.app.connect_to_db')
    @patch('exercises.update.app.jwt.decode')
    def test_mysql_error(self, mock_jwt_decode, mock_connect_to_db):
        #test con error de mysql
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = pymysql.MySQLError("MySQL error")

        event = {
            'body': json.dumps({
                'exercise_id': '1',
                'name': 'Levantamiento de gluteos',
                'description': 'Descripción actualizada'
            }),
            'headers': {
                'Authorization': 'Bearer validtoken'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Vuelve a intentarlo más tarde.")

if __name__ == '__main__':
    unittest.main()
