import logging
import pymysql
from db_conn import connect_to_db


def register_feedback(user_id, routine_id, feedback_date, score, comment):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO feedback (user_id, routine_id, feedback_date, score, comment) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_insert, (user_id, routine_id, feedback_date, score, comment))

            connection.commit()
            return cursor.lastrowid

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

def get_routine(id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM routine WHERE id = %s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()

def user_is_in_group(userUid, teamId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_group WHERE user_id = %s AND team_id = %s"
            cursor.execute(sql, (userUid, teamId))
            result = cursor.fetchone()

            return result is not None
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
