import unittest

from src.job_process_all_incoming_messages import  job_process_all_recent_conversations,process_conversation_only_segments
from src.ConversationIdStorage import ConversationIdStorage

class TestFunctions(unittest.TestCase):
    

    @unittest.skip("integration tests are skip by default")
    def test_job(self):
        processConversationIds = ConversationIdStorage()
        job_process_all_recent_conversations(60, processConversationIds)

    @unittest.skip("integration tests are skip by default")
    def test_conversation(self):
        conversationId = "" 
        process_conversation_only_segments(conversationId , True)

if __name__ == "__main__":
    unittest.main() 