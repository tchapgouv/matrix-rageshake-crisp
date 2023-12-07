import requests
import os
import psycopg2
from typing import  Dict, List
from dotenv import load_dotenv
from utils import get_auth_headers



def get_conversations(page_number: int) -> List[Dict]:
    #url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/"
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"
    headers = get_auth_headers()

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]

def job_sync_conversations_metabase(conversations_max:int = 0):
    #get last 200 conversations
    # push each conversation to postgres


def metabase_database_connect():
    load_dotenv()
    METABASE_PG_ENDPOINT = os.environ[""]
    METABASE_PG_DATABASE = os.environ[""]
    METABASE_PG_PORT     = os.environ[""]
    METABASE_PG_USER     = os.environ[""]
    METABASE_PG_PASS     = os.environ[""]
    pg_connection_dict = {
        'dbname':   METABASE_PG_DATABASE,
        'user':     METABASE_PG_USER,
        'password': METABASE_PG_PASS,
        'port':     METABASE_PG_PORT,
        'host':     METABASE_PG_ENDPOINT
    }
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**pg_connection_dict)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        return error