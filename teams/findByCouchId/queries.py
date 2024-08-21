import logging
import pymysql
from .db_conn import connect_to_db


def get_team_by_couch_id(couch_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teams WHERE couch_id = %s"
            cursor.execute(sql, (couch_id,))
            result = cursor.fetchone()
            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
