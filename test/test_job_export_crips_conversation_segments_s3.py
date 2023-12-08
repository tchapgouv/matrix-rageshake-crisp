import unittest
from job_export_crips_conversation_segments_s3 import extract_fields

class TestExtractFields(unittest.TestCase):
   
    def test_valid_data(self):
        json_dict ={
                    "session_id": "session_test",
                    "updated_at": 1702031578685,
                    "created_at" : 1702031578685,
                    "meta": {
                        "segments": ["test_segment"]
                    }
                }
           
        expected_result = {
            "session_id": "session_test",
            "updated_at": "2023-12-08 10:32:58",
            "created_at": "2023-12-08 10:32:58",
            "segments": ["test_segment"],
            "state" : "N/A"
        }
        self.assertEqual(extract_fields(json_dict), expected_result)

    # def test_invalid_data(self):
    #     json_dict = {}
    #     expected_result = "No data available or data format incorrect"
    #     self.assertEqual(extract_fields(json_dict), expected_result)

if __name__ == '__main__':
    unittest.main()

