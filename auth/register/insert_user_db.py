import logging
import pymysql
from db_conn import connect_to_db


def insert_user_db(uid, name, lastname, age, gender):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (uid, name, lastname, status, age, gender) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (uid, name, lastname, 'activo', age, gender))
            connection.commit()
            return True
    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


def user_exists_in_db(username):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] > 0
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
