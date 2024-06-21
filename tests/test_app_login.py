from login import app


def test_lambda_handler():
    evento = {
        'email': 'jdrj40@gmail.com',
        'password': 'qwerty1231'
    }

    response = app.lambda_handler(evento, {})
    print(response)
