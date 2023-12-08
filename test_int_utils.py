import unittest

from utils import get_conversations, get_messages
from datetime import datetime, timedelta

class TestFunctions(unittest.TestCase):
    
    @unittest.skip("")
    def test_get_messages(self):
        print(f'coucou')
        messages = get_messages("session_127d6e28-ccfd-4e58-a77a-22a723bc9514")
        print(f'messages : {messages}')

    @unittest.skip("")
    def test_get_sleepy_conversations(self):

        data = get_conversations({
            "filter_not_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : datetime.now() - timedelta(days=7),
            "filter_date_start" : datetime.now() - timedelta(days=10)
        })

        print(data)

    def test_get_resolved_conversations_from_last_week(self):

        data = get_conversations({
            "filter_not_resolved": 1,
            "order_date_updated": 1,
            "filter_date_end" : datetime.now(),
            "filter_date_start" : datetime.now() - timedelta(days=14)
        })

        print(data)


if __name__ == '__main__':
    unittest.main()