import json
import logging
import os
import pymysql
from get_secret import get_secret


def connect_to_db():
    secret = json.loads(get_secret())

    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=secret['username'],
            password=secret['password'],
            database=os.getenv('DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"ERROR: Unexpected error: Could not connect to MySQL instance. {e}")
        raise e
