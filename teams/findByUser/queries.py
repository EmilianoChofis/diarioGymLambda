import logging
import pymysql
from .db_conn import connect_to_db


def get_user(userId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE uid = %s"
            cursor.execute(sql, (userId,))
            result = cursor.fetchone()
            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()

def get_team_from_user(user_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT t.* FROM teams t INNER JOIN user_group ug ON t.id = ug.team_id WHERE ug.user_id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()

def get_couch_by_uid(uid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE uid = %s"
            cursor.execute(sql, (uid,))
            result = cursor.fetchone()
            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
