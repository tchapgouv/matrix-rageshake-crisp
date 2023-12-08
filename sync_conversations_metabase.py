import csv
import requests
import json
from typing import  Dict, List
import os
import datetime

import os
import psycopg2
from psycopg2 import sql
from typing import  Dict, List
from dotenv import load_dotenv
from utils import get_auth_headers
from botocore.client import Config
import boto3
import tempfile

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]
S3_ACCESS_KEY_ID=os.environ["S3_ACCESS_KEY_ID"]
S3_BUCKET_NAME=os.environ["S3_BUCKET_NAME"]
S3_SECRET_ACCESS_KEY=os.environ["S3_SECRET_ACCESS_KEY"]


def get_conversations(page_number: int) -> List[Dict]:
    #url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/"
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"
    headers = get_auth_headers()

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]


def extract_fields(data_dict):
    if "data" in data_dict and data_dict["data"]:
        session_id = data_dict["data"][0].get("session_id", "Not available")
        updated_at = data_dict["data"][0].get("updated_at", "Not available")
        segments = data_dict["data"][0]["meta"].get("segments", "Not available")
        return {
            "session_id": session_id,
            "updated_at": updated_at,
            "segments": segments
        }
    else:
        return "No data available or data format incorrect"

#def job_sync_conversations_metabase(conversations_max:int = 0):
#get last 200 conversations
# push each conversation to postgres

def export_data_to_s3(data):
    # Obtenir la date actuelle pour nommer le fichier
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"conversations_{current_date}.csv"

    # Création d'un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['session_id', 'updated_at', 'segments'])  # CSV header, is it needed?
        for item in data:
            writer.writerow([item['session_id'], item['updated_at'], ', '.join(item['segments'])])

        temp_file_path = temp_file.name

    # S3 connexion 
    s3_client = boto3.client('s3',
                            aws_access_key_id=S3_ACCESS_KEY_ID,
                            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                            endpoint_url='https://s3.gra.cloud.ovh.net',
                            region_name='gra')


    bucket_name = S3_BUCKET_NAME

    # CSV file Upload to S3 bucket
    with open(temp_file_path, 'rb') as data:
        s3_client.upload_fileobj(data, bucket_name, file_name, ExtraArgs={'ContentType': "text/csv"})


#not used, not tested yet
def insert_data(session_id, updated_at, segments, connection_params):
    # Etablir une connexion à la base de données
    conn = metabase_database_connect()
    cursor = conn.cursor()

    # Requête SQL pour insérer des données
    query = sql.SQL("""
        INSERT INTO sessions (session_id, updated_at, segments)
        VALUES (%s, %s, %s)
        ON CONFLICT (session_id) DO UPDATE 
        SET updated_at = EXCLUDED.updated_at, 
            segments = EXCLUDED.segments
    """)


    # Exécution de la requête
    try:
        cursor.execute(query, (session_id, updated_at, segments))
        conn.commit()
        print("Data inserted successfully")
    except psycopg2.Error as e:
        print("Error: ", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def metabase_database_connect():
    load_dotenv()
    METABASE_PG_ENDPOINT = os.environ["METABASE_PG_ENDPOINT"]
    METABASE_PG_DATABASE = os.environ["METABASE_PG_DATABASE"]
    METABASE_PG_PORT     = os.environ["METABASE_PG_PORT"]
    METABASE_PG_USER     = os.environ["METABASE_PG_USER"]
    METABASE_PG_PASS     = os.environ["METABASE_PG_PASS"]
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
