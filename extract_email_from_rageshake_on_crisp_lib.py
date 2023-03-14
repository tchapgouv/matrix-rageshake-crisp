def user_id_to_email(user_id):
    """Converts a Crisp user ID to an email address"""
    username, domain, *_ = user_id.split(':')[-2].split('-')
    domain = domain.split('.')[0]
    return f"{username}@{domain}"
    
def extract_email_from_message(message_content):
    """Extracts an email address from a Crisp message"""
    for line in message_content.split('\n'):
        if 'email' in line.lower():
            email_start = line.find('"') + 1
            email_end = line.find('"', email_start)
            return line[email_start:email_end]
    return None

def extract_user_id_from_message(message_content):
    """Extracts a user ID from a Crisp message"""
    for line in message_content.split('\n'):
        if 'user_id' in line.lower():
            user_id_start = line.find('"') + 1
            user_id_end = line.find('"', user_id_start)
            return line[user_id_start:user_id_end]
    return None