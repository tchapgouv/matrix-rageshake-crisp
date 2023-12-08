import os
import unittest
from unittest.mock import patch
import export_conversations_crisp_s3  # Remplacez par le nom de votre module
from dotenv import load_dotenv
class TestFileUploadToS3(unittest.TestCase):
    
    def test_upload_to_s3(self):

        # load environment variables from .env file
        load_dotenv()

        S3_BUCKET_NAME=os.environ["S3_BUCKET_NAME"]

        # Créez ici des données de test pour le CSV
        data = [
            {"session_id": "123", "updated_at": 1609459200, "segments": ["customer", "friend"]},
            {"session_id": "124", "updated_at": 1609545600, "segments": ["user", "tester"]}
        ]

        # Appelez votre fonction d'envoi de fichier
        export_conversations_crisp_s3.export_data_to_s3(data)  # Remplacez par le nom de votre fonction


if __name__ == '__main__':
    unittest.main()