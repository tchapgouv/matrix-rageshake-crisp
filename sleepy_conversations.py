import os
import re
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv
from ConversationIdStorage import ConversationIdStorage

from utils import get_auth_headers

# load environment variables from .env file
load_dotenv()

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

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

    return response.json()["data"]