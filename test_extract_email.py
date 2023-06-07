import unittest
from extract_email import  extract_email_from_user_id, extract_email_from_message, extract_user_id_from_message, process_conversation,get_invalid_conversations,get_messages

class TestFunctions(unittest.TestCase):
        

    def test_conversation(self):
        conversationId = "session_b825989a-04e7-4cc7-8ee7-3d32f389219e"
        #conversationId = "session_c28bb18b-45c5-420c-ab4f-3dd0a6da713f" #conversion found by email
        #session_56c61974-7189-42ce-be8c-d697457463be/
        conversation = process_conversation(conversationId , True)
        #print(f'conversion : {conversation}')


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
        

    def test_extract_email_from_user_id(self):
        test_cases = [
            ("@aaa.yyy-diplomatie.gouv.fr:agent.diplomatie.tchap.gouv.fr", 
             "aaa.yyy@diplomatie.gouv.fr"),
            ("@ooo.aaa-intradef.gouv.fr:agent.intradef.tchap.gouv.fr", 
             "ooo.aaa@intradef.gouv.fr"),
            ("@ppp-aaa.jjj-ap-hm.fr:agent.social.tchap.gouv.fr", 
             "ppp-aaa.jjj@ap-hm.fr"),
            ("@ppp-aaa.jjj-gendarmerie.interieur.gouv.fr:agent.interieur.tchap.gouv.fr", 
             "ppp-aaa.jjj@gendarmerie.interieur.gouv.fr"),
            ("@mmm.rrr-ac-aix-marseille.fr:agent.education.tchap.gouv.fr", 
             "mmm.rrr@ac-aix-marseille.fr"),
            ("@ppp.lll-ccc-douane.finances.gouv.fr:agent.finances.tchap.gouv.fr", 
             "ppp.lll-ccc@douane.finances.gouv.fr"),
            ("@fff.mmm-intradef.gouv.fr:agent.intradef.tchap.gouv.fr", 
             "fff.mmm@intradef.gouv.fr"),
            ("@mmm.rrr-ac-aix-marseille.fr:agent.education.tchap.gouv.fr", 
             "mmm.rrr@ac-aix-marseille.fr"), 
             ("@ll.fff-ac-toulouse.fr:agent.education.tchap.gouv.fr", 
             "ll.fff@ac-toulouse.fr")
        ]

        for user_id, expected_email in test_cases:
            self.assertEqual(extract_email_from_user_id(user_id), expected_email)

if __name__ == "__main__":
    unittest.main()

if __name__ == '__main__':
    unittest.main()
