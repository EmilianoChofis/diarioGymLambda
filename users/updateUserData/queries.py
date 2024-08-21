import logging
import pymysql
from .db_conn import connect_to_db


def get_user(uid):
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


def modify_user(uid, name, lastname, age, gender):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET name = %s, lastname = %s, age = %s, gender = %s WHERE uid = %s"
            cursor.execute(sql, (name, lastname, age, gender, uid))
            connection.commit()

            return True

    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


