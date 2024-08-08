import jwt


def validate_token(event):
    """
    Valida el token de acceso del usuario y devuelve el token decodificado o un mensaje de error.

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
        # Decodifica el token sin verificar la firma (para desarrollo/testing)
        claims = jwt.decode(access_token, options={"verify_signature": False})
        return claims, None
    except jwt.ExpiredSignatureError:
        return None, "El token ha expirado."
    except jwt.InvalidTokenError as e:
        return None, f"Token inválido: {e}"
    except Exception as e:
        return None, f"Error al validar el token: {e}"


def validate_user_role(access_token, required_roles):
    """
    Valida si el usuario tiene el rol requerido.

    :param access_token: Token de acceso de Cognito
    :param required_roles: Roles requerido (por ejemplo, 'administradores')
    :return: True si el usuario tiene el rol requerido, False en caso contrario
    """
    try:
        claims = jwt.decode(access_token, options={"verify_signature": False})

        roles = claims.get('cognito:groups')

        if roles is None:
            return False

        if required_roles in roles:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al validar el rol del usuario: {e}")
        return False
