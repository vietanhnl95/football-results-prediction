import requests
import json
import sqlalchemy
import os


def create_db_connection():
    """Connect to Database using db url and return the connection engine"""
    # create connection
    conn = sqlalchemy.create_engine('postgresql://postgres@localhost:5432/football')

    # Test connection
    try:
        conn.execute("SELECT 1")
        print('DB connected')
        return conn
    except Exception as e:
        print(e)
        return None
