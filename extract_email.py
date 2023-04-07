import os
import re
import requests
from base64 import b64encode
from typing import Optional, Dict, List

CRISP_IDENTIFIER = os.environ["CRISP_IDENTIFIER"]
CRISP_KEY = os.environ["CRISP_KEY"]
CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]
DEFAULT_EMAIL = os.environ.get("DEFAULT_EMAIL", "rageshake@beta.gouv.fr")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

EMAIL_REGEX = r"email: ?\s*\"([^\"]+)\""


def extract_email_from_message(message: str) -> Optional[str]:
    email_match = re.search(EMAIL_REGEX, message)
    return email_match.group(1) if email_match else None


def get_auth_headers():
    auth_string = f"{CRISP_IDENTIFIER}:{CRISP_KEY}"
    auth_string_b64 = b64encode(auth_string.encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {auth_string_b64}",
        "X-Crisp-Tier": "plugin",
    }

def get_conversations(page_number: int) -> List[Dict]:
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"
    headers = get_auth_headers()
    params = {
        "search_query": DEFAULT_EMAIL,
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
    update_url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{conversation_id}/meta"
    update_payload = {
        "email": email
    }
    headers = get_auth_headers()
    response = requests.patch(update_url, headers=headers, json=update_payload)
    response.raise_for_status()

def process_conversations(conversations: List[Dict]) -> bool:
    for conversation in conversations:
        conversation_id = conversation["session_id"]
        print(f"# Extract data from {conversation_id}")
        messages = get_messages(conversation_id)
        first_message = messages[0]["content"]

        email = extract_email_from_message(first_message)

        if email:
            print(f"will change {email} to {conversation_id}")
            if not DRY_RUN:
                update_email(conversation_id, email)
            if DRY_RUN:
                return True

    return False

def main():
    print("Start Extraction")
    page_number = 1
    while True:
        conversations = get_conversations(page_number)
        if not conversations:
            break

        stop_processing = process_conversations(conversations)
        if stop_processing:
            break
    print("Finish Extraction")

if __name__ == "__main__":
    main()
