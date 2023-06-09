import os
import re
import requests
from base64 import b64encode
from typing import Optional, Dict, List
from dotenv import load_dotenv
from ConversationIdStorage import ConversationIdStorage



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

SEGMENT_SEND_RESPONSE = "bot-send-response"
SEGMENT_CHIFFREMENT = "chiffrement"
SEGMENT_MOT_DE_PASSE = "mot-de-passe"
SEGMENT_INCRISPTION = "inscription"
SEGMENT_AUTRE = "autre"

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


def get_conversation_meta(conversation_id: str) -> dict:
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/meta"
    headers = get_auth_headers()
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # s'assurer que la requête a été réussie
    return response.json()  # renvoie le contenu de la réponse en tant que dictionnaire JSON

def update_conversation_meta(conversation_id: str, email: str = None, segments: list[str] = None) -> None:
    
    #get existing segments, return empty array if no segment
    existing_segments = list(get_conversation_meta(conversation_id)["data"]["segments"])
    
    print(f"update {email} and segment {segments} in {conversation_id} with existing segments {existing_segments}")
    update_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/meta"
    update_payload = {}
    if email: # si email n'est pas None ou vide
        update_payload["email"] = email

    if segments: # si segments n'est pas None ou vide
        update_payload["segments"] = list(set(existing_segments + segments)) # l'ordre n'est pas conservé, il peut changer
    
    headers = get_auth_headers()
    response = requests.patch(update_url, headers=headers, json=update_payload)
    response.raise_for_status()

#written with ai assist
#this function uses custom regex to extract email
#we want to avoid false positive, this is why we dont use a general regexp
def extract_email_from_user_id(user_id):
    # Dictionary mapping domain regex to extraction function
    domain_regexes = {
        r"diplomatie\.gouv\.fr": lambda m: f"{m.group(1)}@diplomatie.gouv.fr",
        r"intradef\.gouv\.fr": lambda m: f"{m.group(1)}@intradef.gouv.fr",
        r"ap-hm\.fr": lambda m: f"{m.group(1)}@ap-hm.fr",
        r"gendarmerie\.interieur\.gouv\.fr": lambda m: f"{m.group(1)}@gendarmerie.interieur.gouv.fr",
        r"interieur\.gouv\.fr": lambda m: f"{m.group(1)}@interieur.gouv.fr",
        r"ac-[-\w\.]+\.fr": lambda m: f"{m.group(1)}@{m.group(2)}",  # Generic rule for domains starting with "ac-"
        r"douane\.finances\.gouv\.fr": lambda m: f"{m.group(1)}@douane.finances.gouv.fr",
        r"finances\.gouv\.fr": lambda m: f"{m.group(1)}@finances.gouv.fr",
        r"dgfip\.finances\.gouv\.fr": lambda m: f"{m.group(1)}@dgfip.finances.gouv.fr",
    }

    for domain_regex, extraction_func in domain_regexes.items():
        match = re.search(fr"@([-\w\.]+)-({domain_regex})", user_id)
        if match:
            return extraction_func(match)

    return None

def extract_segment(message_content: str) -> str:
    # Liste des termes associés au segment 'inscription'
    inscription_terms = ['inscript', 'inscrire', 'compte']
    for term in inscription_terms:
        if term in message_content.lower():
            return SEGMENT_INCRISPTION
    
    # Liste des termes associés au segment 'chiffrement'
    chiffrement_terms = ['clé', 'chiffr', 'clef', 'cléf', 'crypt', 'illisible', 'vérouill', 'verrouill']
    for term in chiffrement_terms:
        if term in message_content.lower():
            return SEGMENT_CHIFFREMENT
    
    # Liste des termes associés au segment 'mot-de-passe'
    chiffrement_terms = ['initialis', 'mot de passe', 'mdp', 'password', 'reset']
    for term in chiffrement_terms:
        if term in message_content.lower():
            return SEGMENT_MOT_DE_PASSE


    return SEGMENT_AUTRE  # Retourne aucun si aucun des termes n'est trouvé

def process_conversation(conversation_id:str, verbose=False) -> bool:
    try:
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

        if not email or email == 'undefined':
            email = extract_email_from_user_id(userId)
        
        if email:
            if not DRY_RUN:
                segment = extract_segment(combined_messages)
                #add segment SEGMENT_SEND_RESPONSE to activate the bot workflow send response
                #this workflow is : "on Segment update - envoie message"
                segments =[segment, SEGMENT_SEND_RESPONSE]
                update_conversation_meta(conversation_id, email, segments)
                return True
        return False
    except Exception as e:
        #do not fail script
        print(f"error in {conversation_id} : {e}")
        return False


def job_process_invalid_rageshake(processConversationIds:ConversationIdStorage, pageMax:int=1):
    
    """
    Process invalid rageshake in conversations by updating the email in it.
    
    Args:
    - processConversationIds: A ConversationIdStorage object containing the IDs of already processed conversations.
    - pageMax: An integer indicating the maximum number of pages to process.
    
    Returns: None
    
    This function retrieves conversations with invalid rageshake from the server and updates them.
    It processes conversations page by page, starting from page 0 and up to pageMax.
    For each conversation with an invalid rageshake, it checks if the conversation has already been processed
    using the given ConversationIdStorage object. If the conversation has not been processed, it updates the
    participant email.
    """
    
    current_page_number = 0
    total_updated_rageshake = 0

    while True:
        if current_page_number >= pageMax:
            break

        
        conversations = get_invalid_conversations(current_page_number) #fails script if can not get invalid conversations
        print(f"In page {current_page_number}, # conversations with invalid rageshake : {len(conversations)}")

        if not conversations:
            break

        for conversation in conversations:
            conversation_id = conversation["session_id"]
            
            #do not process conversation already processed
            if processConversationIds.has(conversation_id):
                print(f"Conversation already processed : {conversation_id}")
            else:    
                if process_conversation(conversation_id): 
                    total_updated_rageshake+=1

                processConversationIds.add(conversation_id)
        
        current_page_number += 1

    print("**** Finish Extraction ****")
    print(f"Invalid rageshake updated {total_updated_rageshake}")
