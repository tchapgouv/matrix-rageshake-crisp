import unittest
from extract_email import  extract_email_from_message, extract_user_id_from_message, process_conversation,get_invalid_conversations,get_messages

class TestFunctions(unittest.TestCase):
        

    def test_conversation(self):
        conversationId = "session_56c61974-7189-42ce-be8c-d697457463be"
        #conversationId = "session_c28bb18b-45c5-420c-ab4f-3dd0a6da713f" #conversion found by email
        #session_56c61974-7189-42ce-be8c-d697457463be/
        conversation = process_conversation(conversationId , True)
        print(f'conversion : {conversation}')


    def test_extract_email_from_message(self):
        message = 'email: "julien.dauphant@beta.gouv.fr"'
        expected_email = 'julien.dauphant@beta.gouv.fr'
        self.assertEqual(extract_email_from_message(message), expected_email)
        
        message = 'email: "user.name+tag@example.com"'
        expected_email = 'user.name+tag@example.com'
        self.assertEqual(extract_email_from_message(message), expected_email)
        
        message = 'email: "firstname.lastname1-2.3.4_5@example.com"'
        expected_email = 'firstname.lastname1-2.3.4_5@example.com'
        self.assertEqual(extract_email_from_message(message), expected_email)
        
    def test_extract_user_id_from_message(self):
        message = 'user_id: "@julien.dauphant-beta.gouv.fr:agent.dinum.tchap.gouv.fr"'
        expected_user_id = '@julien.dauphant-beta.gouv.fr:agent.dinum.tchap.gouv.fr'
        self.assertEqual(extract_user_id_from_message(message), expected_user_id)
        
        message = 'Contact me at user.name+tag@example.com for more info'
        self.assertIsNone(extract_user_id_from_message(message))
        
        message = 'Please respond to firstname.lastname1-2.3.4_5@example.com'
        self.assertIsNone(extract_user_id_from_message(message))
        
if __name__ == '__main__':
    unittest.main()
