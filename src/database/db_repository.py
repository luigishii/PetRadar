import os
import re
import logging
import atexit
from psycopg2 import connect


# DB
db_conn = None

def connect_db():
    global db_conn
    if db_conn is None or db_conn.closed:

        db_host = os.environ.get(f'DB_HOST')
        db_name = os.environ.get(f'DB_NAME')
        db_user = os.environ.get(f'DB_USER')
        db_port = os.environ.get(f'DB_PORT')
        db_password = os.environ.get(f'DB_PASSWORD')

        if not re.match(r'^[a-zA-Z0-9.-]+$', db_host) or \
           not re.match(r'^[a-zA-Z0-9_-]+$', db_name) or \
           not re.match(r'^[a-zA-Z0-9_-]+$', db_user) or \
           not (db_port.isdigit() and 1 <= int(db_port) <= 65535):
            raise ValueError("Invalid database credentials or settings")

        db_conn = connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        logging.debug("Database connection established successfully.")
        atexit.register(lambda: db_conn.close() if db_conn else None)
    return db_conn

def check_db_connection():
    try:
        conn = connect_db()
        conn.close()
        logging.debug("Database connection successful")
        return True
    except Exception as e:
        logging.error("Database connection error: %s", str(e))
        return False







