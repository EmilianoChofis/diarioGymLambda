import jwt


def validate_token(event):
    """
    Valida el token de acceso del usuario y devuelve los claims decodificados o un mensaje de error.

    :param event: Evento de Lambda
    :return: Tuple (claims, error_message) - Claims si el token es válido, error_message si no lo es.
    """
    headers = event.get('headers')

    if headers is None:
        return None, "No se encontraron los headers en la solicitud."

    access_token = headers.get('Authorization')

    if not access_token or not access_token.startswith("Bearer "):
        return None, "El token de acceso es requerido y debe comenzar con 'Bearer '."

    access_token = access_token.split(" ")[1]

    try:
        claims = jwt.decode(access_token, options={"verify_signature": False})
        return claims, None
    except jwt.ExpiredSignatureError:
        return None, "El token ha expirado."
    except jwt.InvalidTokenError as e:
        return None, f"Token inválido: {e}"
    except Exception as e:
        return None, f"Error al validar el token: {e}"


def validate_user_role(claims, required_roles):
    """
    Valida si el usuario tiene al menos uno de los roles requeridos.

    :param claims: Claims decodificados del token
    :param required_roles: Lista de roles requeridos (ejemplo: ['Admin', 'User'])
    :return: True si el usuario tiene al menos uno de los roles requeridos, False en caso contrario
    """
    try:
        roles = claims.get('cognito:groups', [])

        # Verificar si alguno de los roles requeridos está en los roles del usuario
        if any(role in roles for role in required_roles):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al validar el rol del usuario: {e}")
        return False