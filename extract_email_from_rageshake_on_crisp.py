import os
from crisp_api import Crisp

def user_id_to_email(user_id):
    """Converts a Crisp user ID to an email address"""
    user_id_parts = user_id.split(':')
    username, domain, *_ = user_id_parts[0].split('-')
    return f"{username}@{domain}.{user_id_parts[1].split('.')[0]}"

def extract_email_from_message(message):
    """Extracts an email address from a Crisp message"""
    email_start = message.find('"') + 1
    email_end = message.find('"', email_start)
    return message[email_start:email_end]

def extract_user_id_from_message(message):
    """Extracts a user ID from a Crisp message"""
    user_id_start = message.find('"') + 1
    user_id_end = message.find('"', user_id_start)
    return message[user_id_start:user_id_end]

# Load API key and website ID from environment variables
api_key = os.environ.get('CRISP_API_KEY')
website_id = os.environ.get('CRISP_WEBSITE_ID')
email_to_search = os.environ.get('CRISP_EMAIL_TO_SEARCH', 'rageshake@beta.gouv.fr')
only_change_last_one = os.environ.get('CRISP_ONLY_CHANGE_LAST_ONE', '').lower() in ('true', '1')

# Create a Crisp object with the API key
crisp = Crisp(api_key)

# Get all conversations with the state "pending"
conversations = []
page_num = 1
while True:
    page_conversations = crisp.website_conversations.list(website_id, state='pending', page=page_num)['data']
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
        messages = crisp.website_conversations.get_messages(website_id, conversation_id)['data']
        
        # Loop through the messages in reverse order (to get the first message)
        for message in reversed(messages):
            # Check if the message has a "type" of "text" and contains the word "email"
            if message['type'] == 'text' and 'email' in message['content'].lower():
                # Try to extract the email address from the message
                conversation_email = extract_email_from_message(message['content'])
                break
            
            # Check if the message has a "type" of "text" and contains the word "user_id"
            elif message['type'] == 'text' and 'user_id' in message['content'].lower():
                # Try to extract the user ID from the message
                conversation_user_id = extract_user_id_from_message(message['content'])
                break
        
        # If we found a user ID, convert it to an email address
        if conversation_user_id
