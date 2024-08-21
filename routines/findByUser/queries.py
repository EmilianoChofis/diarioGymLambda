import logging
from datetime import datetime

import pymysql
from db_conn import connect_to_db

def get_team_by_id(teamId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teams WHERE id = %s"
            cursor.execute(sql, (teamId,))
            result = cursor.fetchone()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR GETTING TEAM: {e}")
        raise e
    finally:
        connection.close()

def get_users_from_team(teamId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT u.* FROM user_group ug INNER JOIN users u ON ug.user_id = u.uid WHERE ug.team_id = %s"
            cursor.execute(sql, (teamId,))
            result = cursor.fetchall()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR GETTING USERS FROM A TEAM: {e}")
        raise e
    finally:
        connection.close()

def get_user_routines(uid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM routine WHERE user_id = %s"
            cursor.execute(sql, (uid,))
            result = cursor.fetchall()

            # Convertir datetime a string
            for routine in result:
                if isinstance(routine['date'], datetime):
                    routine['date'] = routine['date'].strftime('%Y-%m-%d %H:%M:%S')

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR GETTING USERS ROUTINES: {e}")
        raise e
    finally:
        connection.close()

def get_routine_exercises(routineId):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM routine_exercise re INNER JOIN exercises e ON e.id = re.exercise_id WHERE re.routine_id = %s"
            cursor.execute(sql, (routineId,))
            result = cursor.fetchall()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR GETTING ROUTINE EXERCISES: {e}")
        raise e
    finally:
        connection.close()

def get_user_by_uid(uid):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE uid = %s"
            cursor.execute(sql, (uid,))
            result = cursor.fetchone()

            return result
    except pymysql.MySQLError as e:
        logging.error(f"ERROR GETTING USER BY UID: {e}")
        raise e
    finally:
        connection.close()