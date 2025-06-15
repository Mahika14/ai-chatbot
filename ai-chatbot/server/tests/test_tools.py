import unittest
from unittest.mock import patch, MagicMock
import io

# Important: We need to add the project root to the path so we can import our modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools import find_and_clean_urls, file_processor_tool, url_shortener_tool

class TestTools(unittest.TestCase):

    def test_find_and_clean_urls(self):
        print("Running test: test_find_and_clean_urls")
        text = "Check out https://example.com. Also, see http://test.com/page, and one more (https://another.com/)."
        expected = ['https://example.com', 'http://test.com/page', 'https://another.com/']
        self.assertEqual(find_and_clean_urls(text), expected)

    @patch('tools.url_scraper_tool')
    def test_file_processor_tool_txt(self, mock_scraper_tool):
        print("Running test: test_file_processor_tool_txt")
        mock_scraper_tool.return_value = ("scraped content", None)

        text_content = "This is a test file with a url https://example.com/inside."
        file_stream = io.BytesIO(text_content.encode('utf-8'))
       
        original, scraped = file_processor_tool(file_stream, 'test.txt')
       
        self.assertEqual(original, text_content)
        self.assertIn("scraped content", scraped)
        mock_scraper_tool.assert_called_with('https://example.com/inside')

    @patch('tools.requests.get')
    def test_url_shortener_tool(self, mock_requests_get):
        print("Running test: test_url_shortener_tool")
        # Mock the response from the is.gd API
        mock_response = MagicMock()
        mock_response.text = "https://is.gd/short"
        mock_requests_get.return_value = mock_response

        text = "Here is a long link: https://a-very-long-and-complex-url.com/that-needs-shortening"
        result = url_shortener_tool(text)
       
        self.assertIn("https://is.gd/short", result)
        self.assertNotIn("a-very-long-and-complex-url", result)


if __name__ == '__main__':
    unittest.main()