import unittest
from extract_email import user_id_to_email, extract_email_from_message, extract_user_id_from_message

class TestFunctions(unittest.TestCase):
    def test_user_id_to_email(self):
        user_id = '@julien.dauphant-beta.gouv.fr:agent.dinum.tchap.gouv.fr'
        expected_email = 'julien.dauphant@beta.gouv.fr'
        self.assertEqual(user_id_to_email(user_id), expected_email)
        
        user_id = '@julien.dauphant-ac-paris.fr:agent.dinum.tchap.gouv.fr'
        expected_email = 'julien.dauphant@ac-paris.fr'
        self.assertEqual(user_id_to_email(user_id), expected_email)
        
        user_id = '@julien.dauphant-dgfip.gouv.fr:agent.dinum.tchap.gouv.fr'
        expected_email = 'julien.dauphant@dgfip.gouv.fr'
        self.assertEqual(user_id_to_email(user_id), expected_email)
        
        user_id = '@firstname.lastname1-2.3.4_5-example.com:agent.lol.tchap.gouv.f'
        expected_email = 'firstname.lastname1-2.3.4_5@example.com'
        self.assertEqual(user_id_to_email(user_id), expected_email)
        
        user_id = '@user.name+tag-example.com:agent.intradef.tchap.gouv.fr'
        expected_email = 'user.name+tag@example.com'
        self.assertEqual(user_id_to_email(user_id), expected_email)
        
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
