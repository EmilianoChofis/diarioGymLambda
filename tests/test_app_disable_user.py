from users.disableUser import app


def test_lambda_handler():
    evento = {
        'id': 2
    }
    response = app.lambda_handler(evento, "")
    print(response)
