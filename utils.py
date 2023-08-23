import os
from base64 import b64encode
from dotenv import load_dotenv
from typing import Optional, Dict, List
import requests


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