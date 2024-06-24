from unittest.mock import patch, MagicMock

import pymysql

from auth.login import app
import unittest
import json

# simulacion cuerpo de la peticion
mock_body_login = {
    "body": json.dumps({
        "email": "emi@mail",
        "password": "123"
    })
}
#lista de escenarios
"""
- caso exitoso 200
- caso exitoso sin datos 201
- caso no hay conexion a bd (pero las secrets si)
- caso no se pueden obtener las secrets
- 
"""

class TestAppLogin(unittest.TestCase):

    @patch("auth.login.app.connect_to_db")
    @patch("auth.login.db_conn.get_secret")
    def test_lambda_handler(self, mock_get_secret, mock_connect):
        mock_connection = MagicMock()
        # Mockeamos el cusor, caso particular a nuestro modo de programacion
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.cursor.return_value.__exit__.return_value = False

        # valor del parchado para la conexion
        mock_connect.return_value = mock_connection
        # el valor del parchado a los parametros necesarios para get_secret
        mock_get_secret.return_value = {'username': 'username', 'password': 'password', 'engine': 'mysql',
                                        'host': 'host', 'port': 3306, 'dbInstanceIdentifier': 'utez'}

        # parchado de valor ESPERADO de la consulta fetchOne
        mock_cursor.fetchone.return_value = {'id': 1, 'email': 'emi@mail', 'password': '123'}

        result = app.lambda_handler(mock_body_login, None)
        # con esto debe coincidir tanto statusCode como mensaje y estructura
        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Login exitoso", result['body'])
        print(result)

    @patch("auth.login.app.connect_to_db")
    @patch("auth.login.db_conn.get_secret")
    def test_lambda_handler_connection_failed(self, mock_get_secret, mock_connect):
        mock_connect.side_effect = pymysql.MySQLError({})
        mock_get_secret.return_value = {'username': 'username', 'password': 'password', 'engine': 'mysql',
                                        'host': 'host', 'port': 3306, 'dbInstanceIdentifier': 'utez'}

        result = app.lambda_handler(mock_body_login, None)
        # con esto debe coincidir tanto statusCode como mensaje y estructura
        self.assertEqual(result['statusCode'], 500)
        body = json.loads(result["body"])
        self.assertIn("error", body)
        print(result)
