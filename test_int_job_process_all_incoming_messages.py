import unittest

from src.job_process_all_incoming_messages import  job_process_all_incoming_messages,process_conversation_from_email, is_email_valid
from src.ConversationIdStorage import ConversationIdStorage
from src.utils import setLogLevel

class TestFunctions(unittest.TestCase):
    
    setLogLevel("INFO")

    @unittest.skip("integration tests are skip by default")
    def test_job(self):
        processConversationIds = ConversationIdStorage()
        job_process_all_incoming_messages(10, processConversationIds)

    @unittest.skip("integration tests are skip by default")
    def test_conversation(self):
        conversationId = "session_c237d015-2fd7-41b5-9c68-624846200c37" 
        process_conversation_from_email(conversationId , True)

    @unittest.skip("integration tests are skip by default")
    def test_is_email_valid(self):
        conversationId = "session_8a236767-49aa-4dc2-a41b-8ad961769ee7" 
        self.assertEqual(is_email_valid(conversationId), False)

if __name__ == "__main__":
    unittest.main() 