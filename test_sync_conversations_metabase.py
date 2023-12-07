import unittest
from sync_conversations_metabase import extract_fields

class TestExtractFields(unittest.TestCase):
   
    def test_valid_data(self):
        json_dict = {
            "error": False,
            "reason": "listed",
            "data": [
                {
                    "session_id": "session_test",
                    "updated_at": 1234567890,
                    "meta": {
                        "segments": ["test_segment"]
                    }
                }
            ]
        }
        expected_result = {
            "session_id": "session_test",
            "updated_at": 1234567890,
            "segments": ["test_segment"]
        }
        self.assertEqual(extract_fields(json_dict), expected_result)

    def test_invalid_data(self):
        json_dict = {}
        expected_result = "No data available or data format incorrect"
        self.assertEqual(extract_fields(json_dict), expected_result)

if __name__ == '__main__':
    unittest.main()