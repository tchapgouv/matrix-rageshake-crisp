import unittest

from utils import get_messages

class TestFunctions(unittest.TestCase):
    
    def test_get_messages(self):
        print(f'coucou')
        messages = get_messages("session_127d6e28-ccfd-4e58-a77a-22a723bc9514")
        print(f'messages : {messages}')