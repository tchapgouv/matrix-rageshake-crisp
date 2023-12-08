import os
import re
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List
from dotenv import load_dotenv

from utils import get_auth_headers, get_messages, crisp_url

# load environment variables from .env file
load_dotenv()

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

VERBOSE = True


def job_process_sleepy_conversations(conversations_max:int = 0):
  
    """
    Process sleepy conversation by sending a message and closing the conversation

    A conversation is stated as sleepy when the user hasn't answered our last message within 7 days.
    
    Args:
    - conversations_max: how many max sleepy conversation should be processed, default is 0 (no max)
    
    Returns: None
    """

    print(f'Starting Job of processing sleepy conversation')
    sleepy_conversations = get_sleepy_conversations(conversations_max if conversations_max > 0 else 999999)

    for sleepy_conversation in sleepy_conversations:
        wakeup_sleepy_conversation(sleepy_conversation["session_id"])



def wakeup_sleepy_conversation(conversation_id:str):
    print(f'wakeup sleepy conversation : {crisp_url(conversation_id)}')
    message = """
            *Ceci est un message automatique*

            Bonjour,

            Je reviens vers vous suite à votre sollicitation auprès du support de Tchap.
                        
            Vos difficultés sont-elles résolues à ce jour ?

            Nous restons à votre disposition si besoin.

            Bien cordialement

            NB : Nos applications Android et iPhone évoluent régulièrement, pensez à les mettre à jour.

            """
    
    send_message(conversation_id, message)
    change_conversation_state(conversation_id, "resolved")



def is_last_message_from_operator(conversation_id:str):
    
    messages = get_messages(conversation_id)
    
    #remove notes and others not text messages
    only_text_messages = list(filter(lambda x: x.get('type', '')=='text', messages))

    #get last message
    last_message = only_text_messages[-1]

    return last_message["from"] == "operator"

# get the oldest sleepy conversations
def get_sleepy_conversations(conversations_max:int) -> List[Dict]:
    sleepy_conversations = []

    not_resolved_conversations = get_not_resolved_conversations()
    print(f'Not resolved conversations : {len(not_resolved_conversations)}')

    #loop upon resolved conversations from the oldest to the newest
    for conversation in reversed(not_resolved_conversations):
            
        #avoid spamming crisp, sleep a bit
        time.sleep(1)

        if is_older_than_seven_days(conversation) and is_last_message_from_operator(conversation["session_id"]):
            print(f'sleepy conversation : {crisp_url(conversation["session_id"])}')
            sleepy_conversations.append(conversation)
            if len(sleepy_conversations) >= conversations_max:
                break 
        else:
            print(f'not-resolved-not-sleepy conversation : {crisp_url(conversation["session_id"])}')

    
    return sleepy_conversations
    

#retrieve unresolved conversations older than 7 days. The first item is the newest updated conversation
#todo : refactor to use utils.get_conversations instead
def get_not_resolved_conversations() -> List[Dict]:
    not_resolved_conversations = []
    page_number = 0
    end_looping = False

    # get 7 days old timestamp
    seven_days_ago = datetime.now() - timedelta(days=7)
    hundred_days_ago = datetime.now() - timedelta(days=100)

    #loop over not resolved conversations
    while not end_looping :

        #get not resolved conversations
        url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"

        headers = get_auth_headers()
        params = {
            "filter_not_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : seven_days_ago.isoformat(),
            "filter_date_start" : hundred_days_ago.isoformat()
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        conversations_to_append =  response.json()["data"]
        
        not_resolved_conversations = not_resolved_conversations + conversations_to_append

        #update loop controllers
        end_looping = len(conversations_to_append) == 0
        page_number += 1

        print(f'not resolved conversations : {len(not_resolved_conversations)}')
        #avoid spamming crisp, sleep a bit
        time.sleep(1)

    return not_resolved_conversations



def visitor_has_unread_messages(conversation):
    return conversation["unread"]["visitor"] > 0


def last_message_is_from_us(conversation):
    return conversation["unread"]["visitor"] > 0

def is_older_than_seven_days(conversation):
    timestamp = conversation["updated_at"]/1000

    # Current date
    today = datetime.now()

    # Date from the timestamp
    timestamp_date = datetime.fromtimestamp(timestamp)

    difference = today - timestamp_date

    # Check if the difference is greater than 7 days
    return difference.days > 7

# Need token scope website:conversation:state write
def change_conversation_state(conversation_id, state):
    update_payload = {
        "state" : state
    }

    #state = pending,unresolved, resolved    
    update_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/state"
    headers = get_auth_headers()
    response = requests.patch(update_url, headers=headers, json=update_payload)
    response.raise_for_status()

# Need token scope website:conversation:state read
def get_conversation_state(conversation_id):
    get_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/state"
    headers = get_auth_headers()
    response = requests.get(get_url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["state"]
    

# Need token scope website:conversation:messages write
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

