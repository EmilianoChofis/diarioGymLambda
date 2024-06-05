import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


def db_connection():
    try:
        connection = pymysql.connect(host=os.getenv('HOST'),
                                     user=os.getenv('USER'),
                                     password=os.getenv('PASSWORD'),
                                     database=os.getenv('DATABASE'),
                                     charset=os.getenv('CHARSET'),
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.MySQLError as e:
        print(f"ERROR: {e}")
        return None
