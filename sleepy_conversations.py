import os
import re
import requests
import datetime

from typing import Dict, List
from dotenv import load_dotenv

from utils import get_auth_headers, get_messages

# load environment variables from .env file
load_dotenv()

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

def wakeup_sleepy_conversation(conversation_id:str):
    message = """
            *Ceci est un message automatique*

            Bonjour,

            Je reviens vers vous suite à votre sollicitation auprès du support de Tchap.
            Vos difficultés sont-elles résolues à ce jour ?

            Si un ticket d'anomalie vous a été communiqué, veuillez-vous référer au ticket pour connaître le status de l'anomalie. 

            Nous restons à votre disposition si besoin.

            Bien cordialement"""
    
    send_message(conversation_id, message)
    change_conversation_state(conversation_id, "resolved")



def is_last_message_from_operator(conversation_id:str):
    
    messages = get_messages(conversation_id)
    
    #get last message
    last_message = messages[-1]

    return last_message["from"] == "operator"


def get_sleepy_conversations(page_number: int) -> List[Dict]:
    #get conversation where user has not answered our question for 7 days
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"

    headers = get_auth_headers()
    params = {
        "filter_not_resolved": 1,
        "order_date_updated": 1
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    conversations =  response.json()["data"]
    sleepy_conversations = []
    for conversation in conversations:
            if is_older_than_seven_days(conversation) and is_last_message_from_operator(conversation["session_id"]):
                print(f'sleepy conversation link : https://app.crisp.chat/website/{CRISP_WEBSITE_ID}/inbox/{conversation["session_id"]}')
                sleepy_conversations.append(conversation)

    return sleepy_conversations
    

def visitor_has_unread_messages(conversation):
    return conversation["unread"]["visitor"] > 0


def last_message_is_from_us(conversation):
    return conversation["unread"]["visitor"] > 0

def is_older_than_seven_days(conversation):
    timestamp = conversation["updated_at"]/1000

    # Current date
    today = datetime.datetime.now()

    # Date from the timestamp
    timestamp_date = datetime.datetime.fromtimestamp(timestamp)

    difference = today - timestamp_date

    # Check if the difference is greater than 7 days
    return difference.days > 7

def change_conversation_state(conversation_id, state):
    update_payload = {
        "state" : state
    }

    #state = pending,unresolved, resolved    
    update_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/state"
    headers = get_auth_headers()
    response = requests.patch(update_url, headers=headers, json=update_payload)
    response.raise_for_status()


def get_conversation_state(conversation_id):
    get_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/state"
    headers = get_auth_headers()
    response = requests.get(get_url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["state"]
    


def send_message(conversation_id, content):
    post_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/message"

    # Vos données de message
    data = {
    "type": "text",
    "from": "operator",
    "origin": "email",
    "content": content
    }

    # Paramètres d'en-tête (si vous avez des clés d'API ou d'autres authentifications)
    headers = get_auth_headers()

    # Envoyer la requête POST
    response = requests.post(post_url, json=data, headers=headers)
    response.raise_for_status()

