import os
from base64 import b64encode
from dotenv import load_dotenv
from typing import Optional, Dict, List
import requests
import time
import logging

# load environment variables from .env file
load_dotenv()

CRISP_IDENTIFIER = os.environ["CRISP_IDENTIFIER"]
CRISP_KEY = os.environ["CRISP_KEY"]
CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]

def setLogLevel(logLevel='DEBUG'): 
    LOGLEVEL = os.environ.get('LOGLEVEL', logLevel).upper()
    logging.basicConfig(level=LOGLEVEL)

def get_auth_headers():
    auth_string = f"{CRISP_IDENTIFIER}:{CRISP_KEY}"
    auth_string_b64 = b64encode(auth_string.encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {auth_string_b64}",
        "X-Crisp-Tier": "plugin",
    }

def get_messages(conversation_id: str) -> List[Dict]:
    messages_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/messages/"
    headers = get_auth_headers()
    response = requests.get(messages_url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]


def crisp_url(conversation_id):
    return "https://app.crisp.chat/website/%s/inbox/%s" % (CRISP_WEBSITE_ID, conversation_id)



# Need token scope website:conversation:sessions read
def get_conversation_meta(conversation_id: str) -> dict:
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/meta"
    headers = get_auth_headers()
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # s'assurer que la requête a été réussie
    return response.json()  # renvoie le contenu de la réponse en tant que dictionnaire JSON

def get_conversation_email(conversation_id: str) -> Optional[str]:
    meta = get_conversation_meta(conversation_id=conversation_id)
    try:
        return meta['data']['email']
    except:
        return None

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

def get_conversations(params) -> List[Dict]:

    """
    Retrieve multiple conversations that match "params" defined in :https://docs.crisp.chat/references/rest-api/v1/#list-conversations
    example :
    
    
    Args:
    - params: params retrieve unresolved conversations older between 7 days and 100 days

    seven_days_ago = datetime.now() - timedelta(days=7)
    hundred_days_ago = datetime.now() - timedelta(days=100)
    params = {
            "filter_not_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : seven_days_ago.isoformat(),
            "filter_date_start" : hundred_days_ago.isoformat()
    }

    
    Returns: List[Dict] of raw conversations defined here https://docs.crisp.chat/references/rest-api/v1/#list-conversations
    """

    matching_conversations = []
    page_number = 0
    end_looping = False

    #loop over not resolved conversations
    while not end_looping :

        #get not resolved conversations
        url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"

        headers = get_auth_headers()

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        conversations_to_append =  response.json()["data"]
        
        matching_conversations = matching_conversations + conversations_to_append

        #update loop controllers
        end_looping = len(conversations_to_append) == 0
        page_number += 1

        logging.debug(f'matching conversations : {len(matching_conversations)}')
        #avoid spamming crisp, sleep a bit
        time.sleep(1)

    return matching_conversations




# Need token scope website:conversation:sessions write
def update_conversation_meta(conversation_id: str, email: str = None, segments: list[str] = None) -> None:
    
    #get existing segments, return empty array if no segment
    existing_segments = list(get_conversation_meta(conversation_id)["data"]["segments"])
    
    logging.debug(f"update {email} and segment {segments} in {conversation_id} with existing segments {existing_segments}")
    update_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/meta"
    update_payload = {}
    if email: # si email n'est pas None ou vide
        update_payload["email"] = email

    if segments: # si segments n'est pas None ou vide
        update_payload["segments"] = list(set(existing_segments + segments)) # l'ordre n'est pas conservé, il peut changer
    
    headers = get_auth_headers()
    response = requests.patch(update_url, headers=headers, json=update_payload)
    response.raise_for_status()

# Is the last message of the conversation from our team (operator)
def is_last_message_from_operator(conversation_id:str):
    
    messages = get_messages(conversation_id)
    
    #remove notes and others not text messages
    only_text_messages = list(filter(lambda x: x.get('type', '')=='text', messages))

    #get last message
    last_message = only_text_messages[-1]

    return last_message["from"] == "operator"


# Are all messages from the Tchap user, ie Tchap Staff hasn't answered yet
def has_tchap_team_answered(conversation_id:str):
    
    messages = get_messages(conversation_id)
    
    #remove notes and others not text messages
    only_text_messages = list(filter(lambda x: x.get('type', '')=='text', messages))

    has_tchap_team_answered= False

    #get last message
    for only_text_message in only_text_messages:
        if only_text_message["from"] == "operator":
            has_tchap_team_answered = True

    return has_tchap_team_answered
