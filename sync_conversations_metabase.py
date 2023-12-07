import requests

from typing import  Dict, List

from utils import get_auth_headers



def get_conversations(page_number: int) -> List[Dict]:
    #url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/"
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"
    headers = get_auth_headers()

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]

def job_sync_conversations_metabase(conversations_max:int = 0):
    #get last 200 conversations