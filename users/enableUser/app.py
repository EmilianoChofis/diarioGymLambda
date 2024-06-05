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
            sql = f"UPDATE users SET expire_at = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 30 DAY), enable = '1' WHERE id = {id}";
            cursor.execute(sql, (id))
            connection.commit()
            response = {
                'statusCode': 200,
                'body': json.dumps({'message': 'User was enabled successfully'})
            }
            return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

    finally:
        connection.close()
