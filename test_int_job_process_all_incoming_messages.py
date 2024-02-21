import unittest

from src.job_process_all_incoming_messages import \
    job_process_all_incoming_messages, \
        process_conversation_from_email, \
        is_email_valid, \
        extract_domain_from_email
from src.job_process_invalid_rageshake import \
    extract_email_from_message, \
    extract_user_id_from_message, \
    extract_email_from_user_id
from src.ConversationIdStorage import ConversationIdStorage
from src.utils import setLogLevel, get_messages, get_conversation_email
import logging

class TestFunctions(unittest.TestCase):
    
    setLogLevel("INFO")

    @unittest.skip("integration tests are skip by default")
    def test_job(self):
        processConversationIds = ConversationIdStorage()
        job_process_all_incoming_messages(10, processConversationIds)

    @unittest.skip("integration tests are skip by default")
    def test_conversation(self):
        conversationId = "session_c17f9280-f854-438b-87b1-da6ea67d2bb4" 
        process_conversation_from_email(conversationId , True)

    @unittest.skip("integration tests are skip by default")
    def test_is_email_valid(self):
        conversationId = "session_8a236767-49aa-4dc2-a41b-8ad961769ee7" 
        self.assertEqual(is_email_valid(conversationId), False)

    #@unittest.skip("integration tests are skip by default")
    def test_is_domain_ok(self):
        conversationId = "session_fd59c44f-f60e-48ea-916c-0bfeebd20f03" 
        messages = get_messages(conversationId)
        message_contents = list(map(lambda message: str(message["content"]), messages)) 
        combined_messages = "".join(message_contents).replace("\n","")  
        email = extract_email_from_message(combined_messages)

        if not email or email == 'undefined':
            email = get_conversation_email(conversationId)

        self.assertEqual(extract_domain_from_email(email), "dgfip.finances.gouv.fr")

if __name__ == "__main__":
    unittest.main() 