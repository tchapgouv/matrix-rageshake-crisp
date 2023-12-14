import os
from dotenv import load_dotenv
from src.ConversationIdStorage import ConversationIdStorage
from datetime import datetime, timedelta

from src.job_process_invalid_rageshake import process_conversation, extract_segment
from src.utils import has_tchap_team_answered, get_conversation_meta, get_conversations, get_messages, update_conversation_meta


SEGMENT_SEND_RESPONSE = "bot-send-response"

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



def job_process_all_incoming_messages(from_minutes:int, processConversationIds:ConversationIdStorage):
    """
    Process not answered conversations by updating the email in it and setting segments
    An additional segment is set to trigger the send of the email
    
    Args:
    - processConversationIds: A ConversationIdStorage object containing the IDs of already processed conversations.
    - from_minutes: conversations will be gathered from a timestamp-from_minutes. Ie 20
    
    Returns: None
    """

    # get conversations from last 20 minutes
    recent_conversations = get_conversations({
            "filter_date_end" : datetime.now(),
            "filter_date_start" : datetime.now() - timedelta(hours=1, minutes=from_minutes) #timezone...
        })
    
    for conversation in recent_conversations:
            conversation_id = conversation["session_id"]
            
            conversation_meta = get_conversation_meta(conversation_id)["data"]
            conversation_email = conversation_meta['email']

            if not processConversationIds.has(conversation_id) and not has_tchap_team_answered(conversation_id):
                #if email is not correct
                if conversation_email==DEFAULT_EMAIL:
                    process_conversation(conversation_id, True)
                else:
                    #if email is correct
                    process_conversation_only_segments(conversation_id, True)
                
                processConversationIds.add(conversation_id)


# process a conversation 
# if email is invalid (rageshake) it is reset
# segments are set in conversation
# An additional segment SEGMENT_SEND_RESPONSE is set to trigger the send of the email
# this method is copied from "job_process_invalid_rageshake.process_conversation"
# should be refactored
def process_conversation_only_segments(conversation_id:str, verbose=False) -> bool:
    try:
        if verbose: 
            print(f"# Extract data from {conversation_id}")
        messages = get_messages(conversation_id)
        #first_message = messages[0]["content"]
        message_contents = list(map(lambda message: str(message["content"]), messages))  # Extract the "content" field from each message
        combined_messages = "".join(message_contents).replace("\n","")  # Concatenate the message contents together into a single string

        if verbose: 
            print(f"all messages : {combined_messages}")


        # if email of user is correct (not the default one) continue with segments
        print(f"Email is correct in conversation : {conversation_id}")
        segment = extract_segment(combined_messages)
        #add segment SEGMENT_SEND_RESPONSE to activate the bot workflow send response
        #this workflow is : "on Segment update - envoie message"
        segments =[segment, SEGMENT_SEND_RESPONSE]
        # conversation should be in "unresolved" state before updating segments
        # change_conversation_state(conversation_id, "unresolved")
        update_conversation_meta(conversation_id=conversation_id, segments=segments)
        return True
    except Exception as e:
        #do not fail script
        print(f"error in {conversation_id} : {e}")
        return False  