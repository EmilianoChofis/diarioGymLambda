import json
from db_conn import connect_to_db


def lambda_handler(event, __):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps('Petición inválida. no se encontró el body.')
        }

    data = json.loads(body)

    user_id = data.get('id')
    connection = connect_to_db()

    try:
        with connection.cursor() as cursor:
            sql = "SELECT username, email, role_id, enable FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            connection.commit()
            if result:
                response = {
                    'statusCode': 200,
                    'body': json.dumps(result)
                }
            else:
                response = {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'User not found'})
                }

            return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

    finally:
        connection.close()
