import logging
import pymysql
from .db_conn import connect_to_db


def remove_user_team(userId, teamId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_insert = "DELETE FROM user_group WHERE user_id = %s AND team_id = %s"
            cursor.execute(sql_insert, (userId, teamId))
            connection.commit()

            return True

    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"ERROR DELETED: {e}")
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


def user_has_team(userId, teamId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_group WHERE user_id = %s AND team_id = %s"
            cursor.execute(sql, (userId, teamId))
            result = cursor.fetchone()

            return result is not None
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


def get_team_by_id(teamId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teams WHERE id = %s"
            cursor.execute(sql, (teamId,))
            result = cursor.fetchone()
            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
