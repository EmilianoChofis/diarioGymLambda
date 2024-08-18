import logging
import pymysql
from .db_conn import connect_to_db


def insert_team_db(uid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO teams (couch_id) VALUES (%s)"
            cursor.execute(sql_insert, (uid,))
            team_id = cursor.lastrowid

            if team_id == 0:
                raise pymysql.MySQLError("No se pudo registrar el equipo.")

            # Confirmar la transacción
            connection.commit()

            return team_id
    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"ERROR REGISTER: {e}")
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

            return result is not None
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
