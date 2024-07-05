import json

from users.disableUser import app

mock_body = {
    "body": json.dumps(
        {
            "id": 3
        })
}


class TestDisable:
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        print(result)
