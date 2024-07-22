from auth.register import app


def test_lambda_handler():
    evento = {
        'name': 'Emiliano',
        'lastname': 'Gonzalez',
        'username': 'emi',
        'email': 'emi@mail',
        'age': 20,
        'gender': 'M',
        'role': 'admin'
    }
    response = app.lambda_handler(evento, {})
    print(response)
