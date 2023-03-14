import os
from crisp_api import Crisp

from extract_email_from_rageshake_on_crisp_lib import user_id_to_email, extract_email_from_message, extract_user_id_from_message

# Load API key and website ID from environment variables
identifier = os.environ.get('CRISP_IDENTIFIER')
api_key = os.environ.get('CRISP_API_KEY')
website_id = os.environ.get('CRISP_WEBSITE_ID')
email_to_search = os.environ.get('CRISP_EMAIL_TO_SEARCH', 'rageshake@beta.gouv.fr')
only_change_last_one = os.environ.get('CRISP_ONLY_CHANGE_LAST_ONE', '').lower() in ('true', '1')

# Create a Crisp object with the API key
crisp = Crisp()
crisp.set_tier("plugin")
crisp.authenticate(identifier, api_key)

# Get all conversations with the state "pending"
conversations = []
page_num = 1
while True:
    page_conversations = crisp.website.search_conversations(website_id, page_num, filter_unread="1")['data']
    if not page_conversations or only_change_last_one:
        break
    conversations += page_conversations
    page_num += 1

# Loop through the conversations
for conversation in reversed(conversations):
    if only_change_last_one and conversation != conversations[-1]:
        continue
    conversation_id = conversation['id']
    conversation_email = None
    conversation_user_id = None
    
    # Check if the conversation has a "meta" object and the "email" key matches the email to search for
    if 'meta' in conversation and conversation['meta'].get('email') == email_to_search:
        # Get the conversation messages
        messages = crisp.website.get_messages_in_conversation(website_id, conversation_id)['data']
        
        message = reversed(messages)[0]:

        if message['type'] != 'text':
            continue
        if not conversation_email:
            conversation_email = extract_email_from_message(message['content'])
        if not conversation_user_id:
            conversation_user_id = extract_user_id_from_message(message['content'])
        if conversation_email and conversation_user_id:
            break
        
        # If we found a user ID, convert it to an email address
        if conversation_user_id:
            conversation_email = extract_user_id_from_message(message['content'])

        # If we found an email address, set it as the conversation email
        if conversation_email:
            crisp.website.update_conversation_metas(website_id, conversation_id, email=conversation_email)