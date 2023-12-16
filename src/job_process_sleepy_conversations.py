import os
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List
from dotenv import load_dotenv
import logging
from src.utils import get_auth_headers, crisp_url, change_conversation_state, is_last_message_from_operator

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
    logging.info(f'Start job_process_sleepy_conversations with conversations_max : {conversations_max}')

    sleepy_conversations = get_sleepy_conversations(conversations_max if conversations_max > 0 else 999999)

    for sleepy_conversation in sleepy_conversations:
        conversation_id = sleepy_conversation["session_id"]
        logging.info(f'Wakeup_sleepy_conversation : {crisp_url(conversation_id)}')
        wakeup_sleepy_conversation(conversation_id)

    #logging.info(f'End job_process_sleepy_conversations')




def wakeup_sleepy_conversation(conversation_id:str):
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




# get the oldest sleepy conversations
def get_sleepy_conversations(conversations_max:int) -> List[Dict]:
    sleepy_conversations = []

    not_resolved_conversations = get_not_resolved_conversations()
    logging.debug(f'Not resolved conversations : {len(not_resolved_conversations)}')

    #loop upon resolved conversations from the oldest to the newest
    for conversation in reversed(not_resolved_conversations):
            
        #avoid spamming crisp, sleep a bit
        time.sleep(1)

        if is_older_than_seven_days(conversation) and is_last_message_from_operator(conversation["session_id"]):
            logging.debug(f'sleepy conversation : {crisp_url(conversation["session_id"])}')
            sleepy_conversations.append(conversation)
            if len(sleepy_conversations) >= conversations_max:
                break 
        else:
            logging.debug(f'not-resolved-not-sleepy conversation : {crisp_url(conversation["session_id"])}')

    
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

        logging.debug(f'not resolved conversations : {len(not_resolved_conversations)}')
        #avoid spamming crisp, sleep a bit
        time.sleep(1)

    return not_resolved_conversations

def is_older_than_seven_days(conversation):
    timestamp = conversation["updated_at"]/1000

    # Current date
    today = datetime.now()

    # Date from the timestamp
    timestamp_date = datetime.fromtimestamp(timestamp)

    difference = today - timestamp_date

    # Check if the difference is greater than 7 days
    return difference.days > 7


    

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

