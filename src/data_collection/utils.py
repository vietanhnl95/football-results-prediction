import requests
import json
import yaml
import sqlalchemy
import os

def create_db_connection(db_url):
    """Connect to Database using db url and return the connection engine"""
    # Connect
    conn = sqlalchemy.create_engine(db_url)

    # Test connection
    try:
        conn.execute("SELECT 1")
        print('DB connected')
        return conn
    except Exception as e:
        print(e)
        return None


def get_api_response(url, querystring=None):
    # get secrets from envionment
    API_KEY = os.getenv('FOOTBALL_API_KEY')

    # request
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': API_KEY
        }
    if querystring is not None:
        response = requests.request("GET", url, headers=headers, params=querystring)
    else:
        response = requests.request("GET", url, headers=headers)

    # check response
    if response.status_code == 200:
        print('API request successfully')
        return json.loads(response.text)
    else:
        print(response.status_code)
        return None


def read_config():
    """Read yaml file and return the config as a dictionary"""
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config
