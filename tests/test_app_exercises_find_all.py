import unittest
from unittest.mock import patch, MagicMock
import json
import pymysql
import jwt
from exercises.find_all.app import lambda_handler  # Ajusta la ruta según tu estructura de proyecto

class TestLambdaHandler(unittest.TestCase):

    @patch('exercises.find_all.app.connect_to_db')
    @patch('exercises.find_all.app.close_connection')
    @patch('exercises.find_all.app.get_all')
    @patch('exercises.find_all.app.jwt.decode')
    def test_successful_query_with_admin_role(self, mock_jwt_decode,mock_get_all,mock_close_connection, mock_connect_to_db):
        # Simulando que el token JWT es válido y contiene el rol 'Admin'
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}

        # Simulando una conexión de base de datos exitosa

        mock_get_all.return_value = [{'id': 1, 'name': 'Pesas'}]
        mock_connect_to_db.return_value = True
        event = {
            "headers": {
                "Authorization": "Bearer Tokenxd"
            }
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Consulta exitosa.")
        self.assertEqual(json.loads(response['body'])['data'], [{'id': 1, 'name': 'Pesas'}])

    @patch('exercises.find_all.app.connect_to_db')
    @patch('exercises.find_all.app.jwt.decode')
    def test_missing_permissions(self, mock_jwt_decode, mock_connect_to_db):
        # Simulando que el token JWT es inválido o no contiene los roles requeridos
        mock_jwt_decode.return_value = {'cognito:groups': ['RoleCualquiera']}  # Rol sin permisos

        event = {
            "headers": {
                "Authorization": "Bearer EljosaToken"
            }
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('exercises.find_all.app.connect_to_db')
    @patch('exercises.find_all.app.jwt.decode')
    def test_database_connection_error(self, mock_jwt_decode, mock_connect_to_db):
        # simulacion de tken y grupos correctos
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}

        # pero con error de conexión a la base de datos
        mock_connect_to_db.return_value = None

        event = {
            "headers": {
                "Authorization": "Bearer Holacoco"
            }
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. No se pudo conectar a la base de datos. Inténtalo más tarde.")

    @patch('exercises.find_all.app.connect_to_db')
    @patch('exercises.find_all.app.jwt.decode')
    def test_missing_authorization_header(self, mock_jwt_decode, mock_connect_to_db):
        #simulacion  sin encabezado de autorización
        event = {}

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('exercises.find_all.app.connect_to_db')
    @patch('exercises.find_all.app.jwt.decode')
    def test_invalid_token_format(self, mock_jwt_decode, mock_connect_to_db):
        #simulacion token inválido
        event = {
            "headers": {
                "Authorization": "Invalid token"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")


    @patch('exercises.find_all.app.close_connection')
    @patch('exercises.find_all.app.get_all')
    @patch('exercises.find_all.app.connect_to_db')
    @patch('exercises.find_all.app.jwt.decode')
    def test_database_query_error(self, mock_jwt_decode, mock_connect_to_db,mock_get_all,mock_close_connection):
        # token valido y en grupo Admin
        mock_jwt_decode.return_value = {'cognito:groups': ['Admin']}

        # Simulando una consulta erronea
        mock_connect_to_db.return_value = True
        mock_get_all.side_effect = pymysql.MySQLError("Error en la consulta.")

        event = {
            "headers": {
                "Authorization": "Bearer josatoken"
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Vuelve a intentarlo más tarde. Error en la consulta.")

if __name__ == '__main__':
    unittest.main()
