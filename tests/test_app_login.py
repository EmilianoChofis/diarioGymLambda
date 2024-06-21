import unittest
import json
from unittest.mock import patch

import pymysql
from botocore.exceptions import ClientError
from pymysql import MySQLError

import auth.login.app
from auth.login import app

mock_body = {
    "body": json.dumps({
        "email": "user",
        "password": "1234"
    })
}


class TestAppLogin(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        self.assertEqual(result['statusCode'], 200)

    @patch.dict("os.environ", {"REGION_NAME": "us-east-2", "DATA_BASE": "bd"})
    @patch("auth.login.app")
    @patch("pymysql.connect")
    def test_lambda_fail(self, mock_connect, __):
        mock_connect.side_effect = ClientError('Error en el servidor al intentar el login.')
        result = app.lambda_handler(mock_body, None)
        self.assertEqual(result['statusCode'], 500)
        body = json.loads(result['body'])
        self.assertIn("error", body)
        self.assertEqual(body['error'], 'Error en el servidor al intentar el login.')
