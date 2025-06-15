import unittest
from unittest.mock import patch
import json

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        """Set up the test client and mock external dependencies."""
        print("Setting up for a Flask app test")
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.kb_patch = patch('app.kb')
        self.llm_patch = patch('app.llm')
        self.mock_kb = self.kb_patch.start()
        self.mock_llm = self.llm_patch.start()
   
    def tearDown(self):
        """Stop the patches."""
        self.kb_patch.stop()
        self.llm_patch.stop()

    def test_index_route(self):
        print("Running test: test_index_route")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_chat_with_kb_query(self):
        print("Running test: test_chat_with_kb_query")
        self.mock_kb.query.return_value = ["context from a document"]
        self.mock_llm.invoke.return_value.content = "This is the AI's answer."

        response = self.client.post('/chat',
            data=json.dumps({'query': 'A question for the documents'}),
            content_type='application/json')
       
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['response'], "This is the AI's answer.")
        self.mock_kb.query.assert_called_with('A question for the documents')


if __name__ == '__main__':
    unittest.main()