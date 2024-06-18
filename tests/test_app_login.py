import unittest
import json

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
