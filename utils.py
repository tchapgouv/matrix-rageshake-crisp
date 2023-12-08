import os
from base64 import b64encode
from dotenv import load_dotenv
from typing import Optional, Dict, List
import requests
import time


# load environment variables from .env file
load_dotenv()

CRISP_IDENTIFIER = os.environ["CRISP_IDENTIFIER"]
CRISP_KEY = os.environ["CRISP_KEY"]
CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]


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

        print(f'matching conversations : {len(matching_conversations)}')
        #avoid spamming crisp, sleep a bit
        time.sleep(1)

    return matching_conversations