import os
import re
import requests
from base64 import b64encode
from typing import Optional, Dict, List
from dotenv import load_dotenv


"""
This script is meant to be run every minute or so by a cron job
Its goal is to search for conversations in script which contains the rageshake@beta.gouv.fr 
and to replace it by the real email of the participant if it can be found in the discussion fields
"""


# load environment variables from .env file
load_dotenv()

CRISP_IDENTIFIER = os.environ["CRISP_IDENTIFIER"]
CRISP_KEY = os.environ["CRISP_KEY"]
CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]
DEFAULT_EMAIL = os.environ.get("DEFAULT_EMAIL", "rageshake@beta.gouv.fr")
DEFAULT_EMAIL = os.environ.get("RAGESHAKE_NAME", "Tchap Rageshake")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

EMAIL_REGEX = r"email: ?\s*\"([^\"]+)\""
USER_ID_REGEX = r"user_id: ?\s*\"([^\"]+)\""

def extract_email_from_message(message: str) -> Optional[str]:
    if not isinstance(message, str):
        return;

    email_match = re.search(EMAIL_REGEX, message)
    #print(f"regex email match {email_match}")
    return email_match.group(1) if email_match else None

def extract_user_id_from_message(message: str) -> Optional[str]:
    if not isinstance(message, str):
        return;
    user_id_match = re.search(USER_ID_REGEX, message)
    return user_id_match.group(1) if user_id_match else None

def get_auth_headers():
    auth_string = f"{CRISP_IDENTIFIER}:{CRISP_KEY}"
    auth_string_b64 = b64encode(auth_string.encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {auth_string_b64}",
        "X-Crisp-Tier": "plugin",
    }

def get_invalid_conversations(page_number: int) -> List[Dict]:
    #url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/"
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"
    headers = get_auth_headers()
    params = {
        "search_query": DEFAULT_EMAIL,
        #"search_query" : "Tchap Rageshake", test to see what this query returns: It returns all conversations with the user Tchap Rageshake
        "search_type": "text",
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()["data"]

def get_messages(conversation_id: str) -> List[Dict]:
    messages_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/messages/"
    headers = get_auth_headers()
    response = requests.get(messages_url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]

def update_email(conversation_id: str, email: str) -> None:
    print(f"update {email} in {conversation_id}")
    update_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/meta"
    update_payload = {
        "email": email
    }
    headers = get_auth_headers()
    response = requests.patch(update_url, headers=headers, json=update_payload)
    response.raise_for_status()


def process_conversation(conversation_id:str, verbose=False) -> bool:
        print(f"# Extract data from {conversation_id}")
        messages = get_messages(conversation_id)
        #first_message = messages[0]["content"]
        message_contents = list(map(lambda message: str(message["content"]), messages))  # Extract the "content" field from each message
        combined_messages = "".join(message_contents).replace("\n","")  # Concatenate the message contents together into a single string

        if verbose: 
            print(f"all messages : {combined_messages}")



        email = extract_email_from_message(combined_messages)
        userId = extract_user_id_from_message(combined_messages)
        print(f"found in {conversation_id}: userId: {userId}, email {email}")

        if email:
            if not DRY_RUN:
                update_email(conversation_id, email)
                return True
        return False


def process_conversations(conversations: List[Dict]) -> int:
    total_updated_rageshake=0
    for conversation in conversations:
        if(process_conversation(conversation["session_id"])):
            total_updated_rageshake+=1
    
    return total_updated_rageshake

def main():
    print("**** Start Extraction ****")
    page_number = 0
    total_invalid_rageshake = 0
    total_updated_rageshake = 0
    while True:
        conversations = get_invalid_conversations(page_number)
        total_invalid_rageshake += len(conversations)
        
        print(f"In page {page_number}, # conversations with invalid rageshake : {len(conversations)}")

        if not conversations:
            break

        total_updated_rageshake += process_conversations(conversations)
        
        page_number += 1

    print("**** Finish Extraction ****")
    print(f"Invalid rageshake found {total_invalid_rageshake}")
    print(f"Invalid rageshake updated {total_updated_rageshake}")
    print(f"Invalid rageshake remaining {total_invalid_rageshake-total_updated_rageshake}")

if __name__ == "__main__":
    main()
