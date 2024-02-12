import unittest
import random
import string

from src.job_process_invalid_rageshake import extract_segment,update_conversation_meta, extract_email_from_user_id, extract_email_from_message, extract_user_id_from_message, extract_platform_from_message, extract_voip_context_from_message, process_conversation_from_rageshake,get_invalid_conversations,get_messages


#utils functions
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class TestFunctions(unittest.TestCase):
    
    def test_inscription_segment(self):
        message_content = random_string(90) + " inscription" + random_string(90)
        self.assertEqual(extract_segment(message_content), 'inscription')

    def test_chiffrement_segment(self):
        message_content = random_string(88) + " chiffré" + random_string(90) 
        self.assertEqual(extract_segment(message_content), 'chiffrement')

    def test_motdepasse_segment(self):
        message_content = random_string(100) + "reinitialisation" + random_string(90)
        self.assertEqual(extract_segment(message_content), 'mot-de-passe')

    def test_autre_segment(self):
        message_content = random_string(100)  # Génère une chaîne de caractères aléatoires de 100 caractères
        self.assertEqual(extract_segment(message_content), 'autre')

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
        
        message = 'email :baba-ac-aix-marseille.fr:agent.education.tchap.gouv.fr'
        expected_user_id = '@baba-beta.gouv.fr:agent.dinum.tchap.gouv.fr'


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

    def test_extract_plateform_from_message(self):
        message = 'User-Agent: "iOS"'
        expected_platform_id = 'ios'
        self.assertEqual(extract_platform_from_message(message), expected_platform_id)

        message = 'User-Agent: "Tchap/2.9.8 (Google Pixel 5; Android 14; UP1A.231105.001; Flavour GooglePlay; MatrixAndroidSdk2 1.6.8)"'
        expected_platform_id = 'android'
        self.assertEqual(extract_platform_from_message(message), expected_platform_id)

        message = 'User-Agent: "undefined"'
        expected_platform_id = 'web'
        self.assertEqual(extract_platform_from_message(message), expected_platform_id)

        message = None
        self.assertIsNone(extract_platform_from_message(message))


    def test_extract_voip_context_from_message(self):
        message = 'User-Agent: "iOS"'
        self.assertIsNone(extract_voip_context_from_message(message))

        message = 'context: "voip"'
        expected_platform_id = 'voip'
        self.assertEqual(extract_voip_context_from_message(message), expected_platform_id)

        message = None
        self.assertIsNone(extract_voip_context_from_message(message))

if __name__ == "__main__":
    unittest.main() 