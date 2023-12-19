import unittest
import random
import string

from src.job_process_invalid_rageshake import  process_conversation_from_rageshake


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
        conversation = process_conversation_from_rageshake(conversation_id=conversationId, verbose=True)
        print(f'conversion : {conversation}')

if __name__ == "__main__":
    unittest.main() 