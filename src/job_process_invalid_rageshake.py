import os
import re
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv
from src.ConversationIdStorage import ConversationIdStorage
import logging
from src.utils import get_auth_headers, get_messages, update_conversation_meta, get_conversation_origin_email
from src.segment_domains import segment_domain_from_email

"""
This script is meant to be run every minute or so by a cron job
Its goal is to search for conversations in script which contains the rageshake@beta.gouv.fr 
and to replace it by the real email of the participant if it can be found in the discussion fields
"""


# load environment variables from .env file
load_dotenv()


CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]
DEFAULT_EMAIL = os.environ.get("DEFAULT_EMAIL", "rageshake@beta.gouv.fr")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

EMAIL_REGEX = r"email: ?\s*\"([^\"]+)\""
USER_ID_REGEX = r"user_id: ?\s*\"([^\"]+)\""

# User-Agent: "Tchap/2.8.4 (samsung SM-A137F; Android 13; TP1A.220624.014.A137FXXS3CWL1; Flavour GooglePlay; MatrixAndroidSdk2 1.5.32)"
# User-Agent: "iOS"
PLATFORM_IOS_REGEX = r"user-agent: \"ios\""
PLATFORM_ANDROID_REGEX = r"user-agent: \"tchap/[0-9\.]*(-dev){0,1} \(.* android [0-9]+; .*\)\""

VOIP_REGEX = r"context: \"voip\""

SEGMENT_SEND_RESPONSE = "bot-send-response"
SEGMENT_CHIFFREMENT = "chiffrement"
SEGMENT_MOT_DE_PASSE = "mot-de-passe"
SEGMENT_INCRISPTION = "inscription"
SEGMENT_AUTRE = "autre"
SEGMENT_NOTIFICATION = "notification"
SEGMENT_SALON = "salon"
SEGMENT_PLATFORM_IOS = "ios"
SEGMENT_PLATFORM_ANDROID = "android"
SEGMENT_PLATFORM_WEB = "web"
SEGMENT_VOIP = "voip"
SEGMENT_AUTO_UISI = "auto-uisi"
SEGMENT_PROCONNECT = "proconnect"

def extract_email_from_message(message: str) -> Optional[str]:
    if not isinstance(message, str):
        return;

    email_match = re.search(EMAIL_REGEX, message)
    #logging.debug(f"regex email match {email_match}")
    return email_match.group(1) if email_match else None

def extract_user_id_from_message(message: str) -> Optional[str]:
    if not isinstance(message, str):
        return;
    user_id_match = re.search(USER_ID_REGEX, message)
    return user_id_match.group(1) if user_id_match else None



# retrieve conversations that have a DEFAULT_EMAIL (typically rageshake email)
def get_invalid_conversations(page_number: int) -> List[Dict]:
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


#written with ai assist
#this function uses custom regex to extract email
#we want to avoid false positive, this is why we dont use a general regexp
def extract_email_from_user_id(user_id):
    if not isinstance(user_id, str):
        return None
    
    # Dictionary mapping domain regex to extraction function
    domain_regexes = {
        r"diplomatie\.gouv\.fr": lambda m: f"{m.group(1)}@diplomatie.gouv.fr",
        r"intradef\.gouv\.fr": lambda m: f"{m.group(1)}@intradef.gouv.fr",
        r"ap-hm\.fr": lambda m: f"{m.group(1)}@ap-hm.fr",
        r"gendarmerie\.defense\.gouv\.fr": lambda m: f"{m.group(1)}@gendarmerie.defense.gouv.fr",
        r"gendarmerie\.interieur\.gouv\.fr": lambda m: f"{m.group(1)}@gendarmerie.interieur.gouv.fr",
        r"interieur\.gouv\.fr": lambda m: f"{m.group(1)}@interieur.gouv.fr",
        r"ac-[-\w\.]+\.fr": lambda m: f"{m.group(1)}@{m.group(2)}",  # Generic rule for domains starting with "ac-"
        r"douane\.finances\.gouv\.fr": lambda m: f"{m.group(1)}@douane.finances.gouv.fr",
        r"finances\.gouv\.fr": lambda m: f"{m.group(1)}@finances.gouv.fr",
        r"dgfip\.finances\.gouv\.fr": lambda m: f"{m.group(1)}@dgfip.finances.gouv.fr",
        r"developpement-durable\.gouv\.fr": lambda m: f"{m.group(1)}@developpement-durable.gouv.fr",
        r"beta\.gouv\.fr": lambda m: f"{m.group(1)}@beta.gouv.fr",
    }

    for domain_regex, extraction_func in domain_regexes.items():
        match = re.search(fr"@([-\w\.]+)-({domain_regex})", user_id)
        if match:
            return extraction_func(match)

    return None

def extract_segment(message_content: str) -> str:

    auto_uisi_terms = ['[element-auto-uisi]']
    for term in auto_uisi_terms:
        if term in message_content.lower():
            return SEGMENT_AUTO_UISI

    # Liste des termes associés au segment 'inscription'
    inscription_terms = ['inscript', 'inscrire', 'compte']
    #suffix = ("-"+suffix if suffix is not None else "")
    for term in inscription_terms:
        if term in message_content.lower():
            return SEGMENT_INCRISPTION

    # Liste des termes associés au segment 'proconnect'
    inscription_terms = ['proco', 'authent']
    #suffix = ("-"+suffix if suffix is not None else "")
    for term in inscription_terms:
        if term in message_content.lower():
            return SEGMENT_PROCONNECT
    
    # Liste des termes associés au segment 'chiffrement'
    chiffrement_terms = ['clé', 'chiffr', 'clef', 'cléf', 'crypte', 'crypté','illisible', 'véroui', 'verroui', 'veroui','vérroui']
    for term in chiffrement_terms:
        if term in message_content.lower():
            return SEGMENT_CHIFFREMENT
    
    # Liste des termes associés au segment 'mot-de-passe'
    chiffrement_terms = ['initialis', 'mot de passe', 'mdp', 'password', 'reset', 'connecter']
    for term in chiffrement_terms:
        if term in message_content.lower():
            return SEGMENT_MOT_DE_PASSE

    # Liste des termes associés au segment 'notification'
    notification_terms = ['notif', 'push', 'alert']
    for term in notification_terms:
        if term in message_content.lower():
            return SEGMENT_NOTIFICATION

# Liste des termes associés au segment 'salon'
    notification_terms = ['salon', 'admin', 'membre', 'extern']
    for term in notification_terms:
        if term in message_content.lower():
            return SEGMENT_SALON

    return SEGMENT_AUTRE  # Retourne aucun si aucun des termes n'est trouvé


def extract_platform_from_message(message_content: str) -> Optional[str]:
    if not isinstance(message_content, str):
        return None

    message_content_lower = message_content.lower()

    platform_match_ios = re.search(PLATFORM_IOS_REGEX, message_content_lower)
    if platform_match_ios:
        return SEGMENT_PLATFORM_IOS
    
    platform_match_android = re.search(PLATFORM_ANDROID_REGEX, message_content_lower)
    if platform_match_android:
        return SEGMENT_PLATFORM_ANDROID

    return SEGMENT_PLATFORM_WEB


def extract_domain_from_email(email: str) -> Optional[str]:
    if not isinstance(email, str):
        return None

    try:
        arobase_index = email.index('@')
    except ValueError:
        return None
    
    domain_lower = email.lower()[arobase_index+1:len(email)]

    return domain_lower


def extract_voip_context_from_message(message_content: str) -> Optional[str]:
    if not isinstance(message_content, str):
        return None

    message_content_lower = message_content.lower()

    platform_match_ios = re.search(VOIP_REGEX, message_content_lower)
    if platform_match_ios:
        return SEGMENT_VOIP

    return None



# process a conversation 
# if email is invalid (rageshake) it is reset
# segments are set in conversation
# An additional segment SEGMENT_SEND_RESPONSE is set to trigger the send of the email
# this method does 2 things, it should be split in two methods
def process_conversation_from_rageshake(conversation_id:str, verbose=False) -> bool:
    try:
        if verbose: 
            logging.debug(f"# Extract data from {conversation_id}")
        
        messages = get_messages(conversation_id)
        #first_message = messages[0]["content"]
        message_contents = list(map(lambda message: str(message["content"]), messages))  # Extract the "content" field from each message
        combined_messages = "".join(message_contents).replace("\n","")  # Concatenate the message contents together into a single string

        if verbose: 
            logging.debug(f"all messages : {combined_messages}")

        email = extract_email_from_message(combined_messages)
        userId = extract_user_id_from_message(combined_messages)

        if not email or email == 'undefined':
            email = extract_email_from_user_id(userId)
        
        if not email or email == 'undefined':
            email = get_conversation_origin_email(conversation_id)
        
        if verbose: 
            logging.debug(f"found in {conversation_id}: userId: {userId}, email {email}")

        if email:
            if not DRY_RUN:
                segment = extract_segment(combined_messages)
                #add segment SEGMENT_SEND_RESPONSE to activate the bot workflow send response
                #this workflow is : "on Segment update - envoie message"
                segments = [segment, SEGMENT_SEND_RESPONSE]
                platform = extract_platform_from_message(combined_messages)
                if platform:
                    segments.append(platform)
                voip_context = extract_voip_context_from_message(combined_messages)
                if voip_context:
                    segments.append(voip_context)
                domain = segment_domain_from_email(email)
                if domain:
                    segments.append(domain)
                update_conversation_meta(conversation_id=conversation_id, email=email, segments=segments)
                return True
        return False
    except Exception as e:
        #do not fail script
        logging.error(f"error in {conversation_id} : {e}")
        return False
    
# deprecated use job_process_all_incoming_messages instead
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
        #logging.debug(f"In page {current_page_number}, # conversations with invalid rageshake : {len(conversations)}")

        if not conversations:
            break

        for conversation in conversations:
            conversation_id = conversation["session_id"]
            
            if not processConversationIds.has(conversation_id):
                if process_conversation_from_rageshake(conversation_id): 
                    total_updated_rageshake+=1

                processConversationIds.add(conversation_id)
            #else:    
                #do not process conversation already processed
                #logging.debug(f"Conversation already processed : {conversation_id}")
        
        current_page_number += 1
