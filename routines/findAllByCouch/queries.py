import logging
import pymysql
from db_conn import connect_to_db


def find_all_by_couch(couchUid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT u.* FROM user_group ug INNER JOIN users u ON ug.user_id = u.uid WHERE ug.team_id = 1"
            cursor.execute(sql, (couchUid,))
            result = cursor.fetchall()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


def user_exists_in_db(uid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE uid = %s"
            cursor.execute(sql, (uid,))
            result = cursor.fetchone()

            return result is not None

    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


def user_has_team(uid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teams WHERE couch_id = %s"
            cursor.execute(sql, (uid,))
            result = cursor.fetchone()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
