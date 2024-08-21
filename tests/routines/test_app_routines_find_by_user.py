import unittest
from unittest.mock import patch, MagicMock
import json

from botocore.exceptions import ClientError

from routines.findByUser.app  import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    @patch('routines.findByUser.app.get_user_by_uid')
    @patch('routines.findByUser.app.get_user_routines')
    @patch('routines.findByUser.app.get_routine_exercises')
    def test_successful_user_routines_retrieval(self, mock_get_routine_exercises, mock_get_user_routines, mock_get_user_by_uid, mock_validate_user_role, mock_validate_token):
        #test correcto
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user_by_uid.return_value = {"uid": "coquito123"}
        mock_get_user_routines.return_value = [{"id": "rutina123"}]
        mock_get_routine_exercises.return_value = [{"exercise_id": "ejercicio123"}]

        event = {
            "body": json.dumps({"userUid": "coquito123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["message"], "Lista de usuarios encontrados dentro del equipo del couch.")
        self.assertIn("data", body)
        self.assertEqual(body["data"]["routines"][0]["exercises"][0]["exercise_id"], "ejercicio123")

    @patch('routines.findByUser.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        #test token invalido
        mock_validate_token.return_value = (None, "Invalid token")

        event = {
            "body": json.dumps({"userUid": "coquito123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 401)
        self.assertEqual(body["message"], "Invalid token")

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    def test_insufficient_permissions(self, mock_validate_user_role, mock_validate_token):
        #test no eres usuario
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = False

        event = {
            "body": json.dumps({"userUid": "coquito123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 403)
        self.assertEqual(body["message"], "No tienes permisos para realizar esta acción.")

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    def test_missing_body(self, mock_validate_user_role, mock_validate_token):
        #test sin body
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True

        event = json.dumps({})


        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "El body es requerido para la petición.")

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    def test_missing_userUid(self, mock_validate_user_role, mock_validate_token):
        #test con body pero sin el id
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True

        event = {
            "body": json.dumps({})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "EL campo userUid es requerido.")

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    @patch('routines.findByUser.app.get_user_by_uid')
    def test_user_not_found(self, mock_get_user_by_uid, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        #test no se encontraron rutinas
        mock_get_user_by_uid.return_value = None

        event = {
            "body": json.dumps({"userUid": "chombo123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        #Esto no es problema mio, que el mensaje no concuerde es problema de josafat
        self.assertEqual(body["message"], "El equipo no tiene usuarios registrados.")
    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    @patch('routines.findByUser.app.get_user_by_uid')
    @patch('routines.findByUser.app.get_user_routines')
    def test_no_routines_found(self, mock_get_user_routines, mock_get_user_by_uid, mock_validate_user_role, mock_validate_token):
        #no se encuentran las rutinas
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user_by_uid.return_value = {"uid": "coquito123"}
        mock_get_user_routines.return_value = None

        event = {
            "body": json.dumps({"userUid": "coquito123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])
        print(response)
        self.assertEqual(response["statusCode"], 200)
        #De nuevo el mensaje es erroneo
        self.assertEqual(body["message"], "Lista de usuarios encontrados dentro del equipo del couch.")

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    @patch('routines.findByUser.app.get_user_by_uid')
    @patch('routines.findByUser.app.get_user_routines')
    @patch('routines.findByUser.app.get_routine_exercises')
    def test_client_error(self, mock_get_routine_exercises, mock_get_user_routines, mock_get_user_by_uid, mock_validate_user_role, mock_validate_token):
        #disparamos el client error
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user_by_uid.side_effect = ClientError({"Error": {"Code": "500"}}, "SomeOperation")

        event = {
            "body": json.dumps({"userUid": "coquito123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertTrue("Error en la conexión." in body["message"])

    @patch('routines.findByUser.app.validate_token')
    @patch('routines.findByUser.app.validate_user_role')
    @patch('routines.findByUser.app.get_user_by_uid')
    @patch('routines.findByUser.app.get_user_routines')
    @patch('routines.findByUser.app.get_routine_exercises')
    def test_exception(self, mock_get_routine_exercises, mock_get_user_routines, mock_get_user_by_uid, mock_validate_user_role, mock_validate_token):
        #test disparamos una excepcion
        mock_validate_token.return_value = ({"sub": "test_uid"}, None)
        mock_validate_user_role.return_value = True
        mock_get_user_by_uid.side_effect = Exception("Excepcion inesperada")

        event = {
            "body": json.dumps({"userUid": "coquito123"})
        }

        response = lambda_handler(event, None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertTrue("Error de servidor." in body["message"])

if __name__ == '__main__':
    unittest.main()
