from auth.set_password import app
import unittest
import json


mock_body = {
    "body": json.dumps({
        "username": "cliente",
        "temporary_password": "y63;ncbR",
        "new_password": "Cliente123?"
    })
}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        print(result)
