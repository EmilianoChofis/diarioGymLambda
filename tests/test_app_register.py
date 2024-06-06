from auth.register import app


def test_lambda_handler():
    evento = {
        'username': 'emi',
        'password': '123456',
        'email': 'emi@mail',
        'role': 'admin'
    }
    response = app.lambda_handler(evento, {})
    print(response)
