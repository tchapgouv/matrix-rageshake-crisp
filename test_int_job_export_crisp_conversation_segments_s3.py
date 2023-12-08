from contextlib import AbstractContextManager
import os
from typing import Any
import unittest
from unittest.mock import patch
import job_export_crips_conversation_segments_s3  # Remplacez par le nom de votre module
from dotenv import load_dotenv
class TestFileUploadToS3(unittest.TestCase):
    
    @unittest.skip("")
    def test_upload_to_s3(self):

        # load environment variables from .env file
        load_dotenv()

        S3_BUCKET_NAME=os.environ["S3_BUCKET_NAME"]

        # Créez ici des données de test pour le CSV
        data = [
            {"session_id": "123", "updated_at": 1702031578685, "segments": ["customer", "friend"]},
            {"session_id": "124", "updated_at": 1702031578685, "segments": ["user", "tester"]}
        ]

        # Appelez votre fonction d'envoi de fichier
        job_export_crips_conversation_segments_s3.export_crisp_conversations_segments_to_s3(data)  # Remplacez par le nom de votre fonction

    #@unittest.skip("")
    def test_job_sync_conversations_metabase(self):
        job_export_crips_conversation_segments_s3.job_export_crips_conversation_segments_s3(200)




if __name__ == '__main__':
    unittest.main()