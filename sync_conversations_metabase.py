import requests
import json
from typing import  Dict, List
import os

from utils import get_auth_headers

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]

def get_conversations(page_number: int) -> List[Dict]:
    #url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/"
    url = f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/{page_number}"
    headers = get_auth_headers()

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]


def extract_fields(data_dict):
    if "data" in data_dict and data_dict["data"]:
        session_id = data_dict["data"][0].get("session_id", "Not available")
        updated_at = data_dict["data"][0].get("updated_at", "Not available")
        segments = data_dict["data"][0]["meta"].get("segments", "Not available")
        return {
            "session_id": session_id,
            "updated_at": updated_at,
            "segments": segments
        }
    else:
        return "No data available or data format incorrect"

