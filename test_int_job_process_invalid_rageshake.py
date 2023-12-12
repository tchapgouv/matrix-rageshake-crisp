import unittest
import random
import string

from src.job_process_invalid_rageshake import extract_segment,update_conversation_meta, extract_email_from_user_id, extract_email_from_message, extract_user_id_from_message, process_conversation,get_invalid_conversations,get_messages


#utils functions
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class TestFunctions(unittest.TestCase):
    
    @unittest.skip("integration tests are skip by default")
    def test_update_conversation(self):
        conversationId = ""
        #update_conversation_meta(conversationId , "test1@test.com", ["test5"])

    @unittest.skip("integration tests are skip by default")
    def test_conversation(self):
        conversationId = ""
        conversation = process_conversation(conversationId , True)
        print(f'conversion : {conversation}')


if __name__ == "__main__":
    unittest.main() 