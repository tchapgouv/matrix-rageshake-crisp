import unittest

from src.utils import \
    get_conversations, \
    get_messages, \
    has_tchap_team_answered, \
    change_conversation_state, \
    get_conversation_state
from datetime import datetime, timedelta

class TestFunctions(unittest.TestCase):
    
    @unittest.skip("integration tests are skip by default")
    def test_change_state(self):
        state = "unresolved"
        session_id = ""
        change_conversation_state(session_id, state)
        new_state = get_conversation_state(session_id)
        print(new_state)
        self.assertEqual(new_state, state)

    @unittest.skip("integration tests are skip by default")
    def test_get_messages(self):
        print(f'coucou')
        session_id = ""
        messages = get_messages(session_id)
        print(f'messages : {messages}')

    @unittest.skip("integration tests are skip by default")
    def test_get_sleepy_conversations(self):

        data = get_conversations({
            "filter_not_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : datetime.now() - timedelta(days=7),
            "filter_date_start" : datetime.now() - timedelta(days=10)
        })

        print(data)

    @unittest.skip("integration tests are skip by default")
    def test_get_resolved_conversations_from_last_week(self):

        data = get_conversations({
            "filter_not_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : datetime.now(),
            "filter_date_start" : datetime.now() - timedelta(days=14)
        })

        print(data)

    @unittest.skip("integration tests are skip by default")
    def test_get_conversations_from_twenty_minutes(self):

        data = get_conversations({
            "filter_date_end" : datetime.now(),
            "filter_date_start" : datetime.now() - timedelta(hours=1, minutes=20) #timezone...
        })

        print(data)

    @unittest.skip("integration tests are skip by default")
    def test_get_unread_conversations(self):
        unread_conversations = get_conversations({"filter_unread":0})


    @unittest.skip("integration tests are skip by default")
    def test_has_tchap_team_answered_yes(self):
        print("test_has_tchap_team_answered : yes")
        self.assertEqual(has_tchap_team_answered("session_f43ac9be-c167-497b-9981-d569abf243dc"), True)

    @unittest.skip("integration tests are skip by default")
    def test_has_tchap_team_answered_no(self):
        print("test_has_tchap_team_answered : no")
        self.assertEqual(has_tchap_team_answered("session_a5d0dff5-4f57-4e58-bef2-05036e2b2493"), False)




if __name__ == '__main__':
    unittest.main()