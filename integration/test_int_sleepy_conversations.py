import unittest
import random
import string
import datetime

from sleepy_conversations import get_sleepy_conversations,change_conversation_state,get_conversation_state, send_message, wakeup_sleepy_conversation, is_last_message_from_operator, job_process_sleepy_conversations
from utils import get_messages

conversation_id = "session_691ea0d5-0543-427b-85dd-95bc412ceb27"

class TestFunctions(unittest.TestCase):
    
    @unittest.skip("integration tests are skip by default, warning this send messages to real conversations")
    def test_job_process_sleepy_conversation(self):
        job_process_sleepy_conversations(10)
    
    @unittest.skip("warning this asks for all not answer conversations to get the sleepy ones")
    def test_get_sleepy_conversation(self):
        max_conversations = 2
        sleepy_conversations = get_sleepy_conversations(max_conversations)
        print(f'sleepy conversations : {len(sleepy_conversations)}')
        self.assertEqual(len(sleepy_conversations), max_conversations)

    @unittest.skip("integration tests are skip by default")
    def test_is_last_message_from_operator(self):
        #this conversation ends with a note from us
        conversation_id = ""
        messages = get_messages(conversation_id)
        print(f'messages : {messages}')
        self.assertEqual(is_last_message_from_operator(conversation_id), False)


    @unittest.skip("integration tests are skip by default")
    def test_must_send_message(self):
       simple_message = "coucou"
       send_message(conversation_id, simple_message)

    @unittest.skip("integration tests are skip by default")
    def test_must_send_multiline_message_with_markdown(self):
       message = """*coucou*
                    
                    ca roule?

                    Moi ca va
                    """
       send_message(conversation_id, message)

    @unittest.skip("integration tests are skip by default")
    def test_must_change_state(self):
        new_state = "pending"
        change_conversation_state(conversation_id, new_state)
        state = get_conversation_state(conversation_id)
        print(state)
        self.assertEqual(state, new_state)

    @unittest.skip("integration tests are skip by default")
    def test_wakeup_sleepy_conversation(self):
        wakeup_sleepy_conversation("session_2e6e0ca1-58cf-4937-b3e5-201cf44a652c")



if __name__ == "__main__":
    unittest.main() 