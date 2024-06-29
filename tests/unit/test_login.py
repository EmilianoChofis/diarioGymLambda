from auth.login import app
import unittest
import json

mock_body = {
    "body": json.dumps({
        "username": "admin",
        "password": "Admin123?"
    })
}


#contraseña enviada a mi correo por cognito 0fTR,PP6

class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        print(result)
