import json

from pycognito import Cognito
import jwt

# usa esto cuando quieras saber sobre el pool de usuarios, por ejemplo la lista de users
#u = Cognito('us-east-1_1HAjH1fKj', '37d6q19su0lg1pjh4d6qca9me7')

# para inicia sesion de un usuario
u_2 = Cognito('your-user-pool-id', 'your-client-id',
              username='bob')

# para cuando ya se autentico el usuario y necesitas una instancia de cognito
u_3 = Cognito('your-user-pool-id', 'your-client-id',
              id_token='your-id-token',
              refresh_token='your-refresh-token',
              access_token='your-access-token')

#si quieres verificar un token
u = Cognito('us-east-1_1HAjH1fKj','37d6q19su0lg1pjh4d6qca9me7',
    id_token='id-token',refresh_token='refresh-token',
    access_token='access-token')
u.verify_tokens()
# See method doc below; may throw an exception

# proceso para registrar un usuario a un pool
# u = Cognito('your-user-pool-id','your-client-id')
# luego le seteas sus valores
#u.set_base_attributes(email='you@you.com', some_random_attr='random value')
# atributos extra
#u.add_custom_attributes(state='virginia', city='Centreville')
# registras
#u.register('username', 'password')

# para autenticar un usuario
# u = Cognito('your-user-pool-id','your-client-id', username='bob')

#u.authenticate(password='bobs-password')
