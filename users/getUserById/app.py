import json

from utils import db_connection


# import requests


def lambda_handler(event, __):

    """
    :param event:
    :param __:
    :return:
    """
    user_id = event['id']
    connection = db_connection()

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
