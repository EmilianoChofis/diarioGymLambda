import json

from utils import db_connection


# import requests


def lambda_handler(event, context):

    """
    :param event:
    :param context:
    :return:
    """
    id = event['id']
    connection = db_connection()

    try:
        with connection.cursor() as cursor:
            sql = f"select * from users WHERE id = {id}"
            cursor.execute(sql, (id))
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
