from users.getUserById import app


def test_lambda_handler_success():
    evento = {
        'id': 1
    }
    context = {}
    response = app.lambda_handler(evento, context)

    # Imprimir la respuesta para verla en la terminal
    print(response)
