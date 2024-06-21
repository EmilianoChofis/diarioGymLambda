import unittest
import json

from botocore.exceptions import ClientError

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

    def test_lambda_fail(self, mock_body):
        mock_body.side_effect = ClientError(error_response={'error': {'msj': 'error 500'}}, operation_name="login")
        result = app.lambda_handler(mock_body, None)
        self.assertEqual(result['statusCode'], 500)
        body = json.loads(result['body'])
        self.assertIn("error", body)
        self.assertEqual(body['error'], 'An error ocurred')
