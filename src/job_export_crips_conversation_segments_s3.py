import csv
import os
import datetime

import os
from src.utils import get_conversations
import boto3
import tempfile
from datetime import datetime, timedelta

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]
S3_ACCESS_KEY_ID=os.environ["S3_ACCESS_KEY_ID"]
S3_BUCKET_NAME=os.environ["S3_BUCKET_NAME"]
S3_SECRET_ACCESS_KEY=os.environ["S3_SECRET_ACCESS_KEY"]

#todo : extract_fields, transform_data and csv.writer "might" be merged to increase readibility
# usecase : I want to add a field easily in the csv 
# usecase : I want to extract another csv from crisp data

#extract fields
def extract_fields(data_dict):

    created_at=  int(data_dict.get("created_at", 0));
    updated_at=   int(data_dict.get("updated_at", 0));

    return {
        "session_id": data_dict.get("session_id", "N/A"),
        "created_at": datetime.utcfromtimestamp(created_at / 1000.0).strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at": datetime.utcfromtimestamp(updated_at / 1000.0).strftime('%Y-%m-%d %H:%M:%S'),
        "state" : data_dict.get("state", "N/A"),
        "segments": data_dict["meta"].get("segments", "N/A")
    }

# transform conversations data
def transform_data(conservations):
    #extract only interesting fields in dataset
    return [extract_fields(data_dict) for data_dict in conservations]

# export a csv that contains all segments in all conversations
# one row in csv per conversation's segment
def export_crisp_conversations_segments_to_s3(data):
    # Obtenir la date actuelle pour nommer le fichier
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"crisp_conversation_segments_{current_date}.csv"

    # Création d'un fichier temporaire csv
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['session_id', 'state', 'segment', 'created_at', 'updated_at'])  # CSV header, is it needed?
        for item in data:
            for segment in item['segments']:
                writer.writerow([item['session_id'], item['state'], segment, item['created_at'], item['updated_at']])

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


def job_export_crips_conversation_segments_s3(max_days_old_conversation):
    """
    
 
    """
    #get conversations from 
    conversations_data = get_conversations({
            #"filter_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : datetime.now(),
            "filter_date_start" : datetime.now() - timedelta(days=max_days_old_conversation)
        })
    
    conversations_data_transformed = transform_data(conversations_data)

    #send to s3
    export_crisp_conversations_segments_to_s3(conversations_data_transformed)

#not used, not tested yet
# def insert_data(session_id, updated_at, segments, connection_params):
#     # Etablir une connexion à la base de données
#     conn = metabase_database_connect()
#     cursor = conn.cursor()

#     # Requête SQL pour insérer des données
#     query = sql.SQL("""
#         INSERT INTO sessions (session_id, updated_at, segments)
#         VALUES (%s, %s, %s)
#         ON CONFLICT (session_id) DO UPDATE 
#         SET updated_at = EXCLUDED.updated_at, 
#             segments = EXCLUDED.segments
#     """)


#     # Exécution de la requête
#     try:
#         cursor.execute(query, (session_id, updated_at, segments))
#         conn.commit()
#         print("Data inserted successfully")
#     except psycopg2.Error as e:
#         print("Error: ", e)
#         conn.rollback()
#     finally:
#         cursor.close()
#         conn.close()

# def metabase_database_connect():
#     load_dotenv()
#     METABASE_PG_ENDPOINT = os.environ["METABASE_PG_ENDPOINT"]
#     METABASE_PG_DATABASE = os.environ["METABASE_PG_DATABASE"]
#     METABASE_PG_PORT     = os.environ["METABASE_PG_PORT"]
#     METABASE_PG_USER     = os.environ["METABASE_PG_USER"]
#     METABASE_PG_PASS     = os.environ["METABASE_PG_PASS"]
#     pg_connection_dict = {
#         'dbname':   METABASE_PG_DATABASE,
#         'user':     METABASE_PG_USER,
#         'password': METABASE_PG_PASS,
#         'port':     METABASE_PG_PORT,
#         'host':     METABASE_PG_ENDPOINT
#     }
#     try:
#         # connect to the PostgreSQL server
#         print('Connecting to the PostgreSQL database...')
#         conn = psycopg2.connect(**pg_connection_dict)
#         return conn
#     except (Exception, psycopg2.DatabaseError) as error:
#         return error
