import logging
from datetime import datetime

import pymysql
from .db_conn import connect_to_db


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


def exercise_exists(exercise_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM exercises WHERE id = %s"
            cursor.execute(sql, (exercise_id,))
            result = cursor.fetchone()

            return result is not None
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()


def register_routine_exercise(routine):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO routine (user_id, date, status) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (routine.get("user").get("id"), routine.get("date"), 'activo'))
            routine_id = cursor.lastrowid

            if routine_id == 0:
                raise pymysql.MySQLError("No se pudo registrar la rutina.")

            for exercise in routine.get("exercises"):
                sql_insert = "INSERT INTO routine_exercise (routine_id, exercise_id, reps, sets) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_insert,
                               (routine_id, exercise.get("id"), exercise.get("reps"), exercise.get("sets")))

            connection.commit()
            return routine_id

    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"ERROR REGISTER: {e}")
        raise e
    finally:
        connection.close()


def routine_exists_today(userUid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM routine WHERE date = %s AND user_id = %s"
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(sql, (today, userUid))
            result = cursor.fetchone()

            return result is not None
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: {e}")
        raise e
    finally:
        connection.close()
