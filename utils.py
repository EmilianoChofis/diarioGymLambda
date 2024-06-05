import pymysql


def db_connection():
    connection = pymysql.connect(host='databaseforlambdas.czssy4oigfcr.us-east-1.rds.amazonaws.com',
                                 user='admin',
                                 password='admin123',
                                 database='utez',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection