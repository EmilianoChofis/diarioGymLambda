import logging
import pymysql
from db_conn import connect_to_db


def get_teams():
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teams"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


def get_users_from_team(team_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT u.* FROM teams t INNER JOIN user_group ug ON t.id = ug.team_id INNER JOIN users u ON ug.user_id = u.uid WHERE t.id = %s"
            cursor.execute(sql, (team_id,))
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
