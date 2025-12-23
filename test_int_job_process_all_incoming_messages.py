import unittest

from src.job_process_all_incoming_messages import \
    job_process_all_incoming_messages, \
    process_conversation_from_email, \
    is_email_valid
from src.job_process_invalid_rageshake import \
    extract_email_from_message, \
    extract_domain_from_email
from src.ConversationIdStorage import ConversationIdStorage
from src.utils import setLogLevel, get_messages, get_conversation_origin_email
from src.segment_domains import segment_domain_from_email

class TestFunctions(unittest.TestCase):
    
    setLogLevel("DEBUG")

    @unittest.skip("integration tests are skip by default")
    def test_job(self):
        processConversationIds = ConversationIdStorage()
        job_process_all_incoming_messages(10, processConversationIds)

    @unittest.skip("integration tests are skip by default")
    def test_conversation(self):
        conversationId = "session_aad0e72b-e9e6-4b13-a6bf-45c2cab916ef" 
        process_conversation_from_email(conversationId , True)

    @unittest.skip("integration tests are skip by default")
    def test_is_email_valid(self):
        conversationId = "session_8a236767-49aa-4dc2-a41b-8ad961769ee7" 
        print("Email: {}".format(get_conversation_origin_email(conversationId)))
        self.assertEqual(is_email_valid(conversationId), False)

    @unittest.skip("integration tests are skip by default")
    def test_is_domain_ok(self):
        conversationId = "session_fd59c44f-f60e-48ea-916c-0bfeebd20f03" 
        messages = get_messages(conversationId)
        message_contents = list(map(lambda message: str(message["content"]), messages)) 
        combined_messages = "".join(message_contents).replace("\n","")  
        email = extract_email_from_message(combined_messages)

        if not email or email == 'undefined':
            email = get_conversation_origin_email(conversationId)

        self.assertEqual(extract_domain_from_email(email), "dgfip.finances.gouv.fr")

    @unittest.skip("integration tests are skip by default")
    def test_domains_tagging(self):
        self.assertIsNone(segment_domain_from_email("john.doe@mondomaine.com"))
        self.assertEqual(segment_domain_from_email("john.doe@dgfip.finances.GOUV.fr"), "dgfip")
        self.assertEqual(segment_domain_from_email("john.doe@finances.gouv.fr"), "finances-autre")
        self.assertEqual(segment_domain_from_email("john.doe@dgccrf.finances.gouv.fr"), "finances-autre")
        self.assertEqual(segment_domain_from_email("john.doe@ac-paris.fr"), "education")
        self.assertEqual(segment_domain_from_email("john.doe@ac-orleans-tours.fr"), "education")
        self.assertEqual(segment_domain_from_email("john.doe@education.gouv.fr"), "education")
        self.assertEqual(segment_domain_from_email("john.doe@ac-polynesie.pf"), "education")
        self.assertEqual(segment_domain_from_email("john.doe@interieur.gouv.fr"), "interieur")
        self.assertEqual(segment_domain_from_email("john.doe@gendarmerie.interieur.gouv.fr"), "gendarmerie")
        self.assertEqual(segment_domain_from_email("john.doe@ch-mortagne.fr"), "social")
        self.assertEqual(segment_domain_from_email("john.doe@chu-grenoble.fr"), "social")
        self.assertEqual(segment_domain_from_email("john.doe@creps-lorraine.sports.gouv.fr"), "social")
        self.assertEqual(segment_domain_from_email("john.doe@economie-solidaire.gouv.fr"), "social")
        self.assertEqual(segment_domain_from_email("john.doe@ints.fr"), "social")
        self.assertEqual(segment_domain_from_email("john.doe@social.gouv.fr"), "social")
        self.assertEqual(segment_domain_from_email("john.doe@intradef.gouv.fr"), "intradef")
        self.assertEqual(segment_domain_from_email("john.doe@justice.gouv.fr"), "justice")
        self.assertEqual(segment_domain_from_email("john.doe@apij-justice.fr"), "justice")
       

if __name__ == "__main__":
    unittest.main() 