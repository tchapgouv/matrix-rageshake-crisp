import unittest

from src.job_process_all_incoming_messages import  job_process_all_incoming_messages,process_conversation_only_segments
from src.ConversationIdStorage import ConversationIdStorage
from src.utils import setLogLevel

class TestFunctions(unittest.TestCase):
    
    setLogLevel("INFO")

    #@unittest.skip("integration tests are skip by default")
    def test_job(self):
        processConversationIds = ConversationIdStorage()
        job_process_all_incoming_messages(10, processConversationIds)

    @unittest.skip("integration tests are skip by default")
    def test_conversation(self):
        conversationId = "session_54315322-66b0-45a3-95a0-1a1671a334ee" 
        process_conversation_only_segments(conversationId , True)

if __name__ == "__main__":
    unittest.main() 