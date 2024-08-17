import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError
from routines.findAllByCouch.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('routines.findAllByCouch.app.validate_token')
    @patch('routines.findAllByCouch.app.validate_user_role')
    @patch('routines.findAllByCouch.app.user_exists_in_db')
    @patch('routines.findAllByCouch.app.user_has_team')
    @patch('routines.findAllByCouch.app.find_all_by_couch')
    def test_successful_case(self, mock_find_all_by_couch, mock_user_has_team, mock_user_exists_in_db,
                             mock_validate_user_role, mock_validate_token):
        #simulacion de que todo sale bien
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = {'teamId': 'team1'}
        mock_find_all_by_couch.return_value = [{'userId': 'Coquito'}, {'userId': 'Josafat'}]

        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'],
                         "Lista de usuarios encontrados dentro del equipo del couch.")
        self.assertIn('data', json.loads(response['body']))

    @patch('routines.findAllByCouch.app.validate_token')
    def test_invalid_token(self, mock_validate_token):
        mock_validate_token.return_value = (None, 'Token inválido.')
        #simulacion token invalido
        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], 'Token inválido.')

    @patch('routines.findAllByCouch.app.validate_token')
    @patch('routines.findAllByCouch.app.validate_user_role')
    def test_invalid_role(self, mock_validate_user_role, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['User']}, None)
        mock_validate_user_role.return_value = False
        #simlacion usuario sin permisos
        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], "No tienes permisos para realizar esta acción.")

    @patch('routines.findAllByCouch.app.validate_token')
    def test_missing_body(self, mock_validate_token):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        event = {
            'body': {}
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "El body es requerido para la petición.")

    def test_missing_couchUid(self):
        #no se envian los headers ni tokens
        event = {
            'body': json.dumps({})
        }

        response = lambda_handler(event, None)
        print(response)

        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontraron los headers en la solicitud.")

    @patch('routines.findAllByCouch.app.user_exists_in_db')
    @patch('routines.findAllByCouch.app.validate_token')
    @patch('routines.findAllByCouch.app.validate_user_role')
    def test_user_not_found(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = False
        #test el couch existe y todo correcto pero no tiene usuarios registrados
        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "No se encontró ningun usuario con ese uid.")

    @patch('routines.findAllByCouch.app.user_exists_in_db')
    @patch('routines.findAllByCouch.app.user_has_team')
    @patch('routines.findAllByCouch.app.validate_token')
    @patch('routines.findAllByCouch.app.validate_user_role')
    def test_no_team(self, mock_validate_user_role, mock_validate_token, mock_user_has_team, mock_user_exists_in_db):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = None
        #el coach no tiene un equipo en la db
        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "El couch no tiene un equipo registrado.")

    @patch('routines.findAllByCouch.app.find_all_by_couch')
    @patch('routines.findAllByCouch.app.user_has_team')
    @patch('routines.findAllByCouch.app.user_exists_in_db')
    @patch('routines.findAllByCouch.app.validate_token')
    @patch('routines.findAllByCouch.app.validate_user_role')
    def test_find_all_by_couch_failure(self, mock_validate_user_role, mock_validate_token, mock_user_exists_in_db,
                                       mock_user_has_team, mock_find_all_by_couch):
        mock_validate_token.return_value = ({'cognito:groups': ['Couch']}, None)
        mock_validate_user_role.return_value = True
        mock_user_exists_in_db.return_value = True
        mock_user_has_team.return_value = {'teamId': 'team1'}
        mock_find_all_by_couch.side_effect = Exception("Error cualquiera")
        #test error cualquier literalmente xd, se dispara el catch por cualquier razon
        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], "Error de servidor. Error cualquiera")

    @patch('routines.findAllByCouch.app.validate_token')
    def test_client_error(self, mock_validate_token):
        mock_validate_token.side_effect = ClientError({'Error': {'Message': 'Client error'}}, 'Operation')
        #TEST DISPARAMOS EL CLIENT ERROR
        event = {
            'body': json.dumps({
                'couchUid': 'Chombo'
            })
        }

        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "Error en la conexión. An error occurred (Unknown) when calling the Operation operation: Client error")


if __name__ == '__main__':
    unittest.main()
