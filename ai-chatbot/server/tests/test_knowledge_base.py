import unittest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We must import the module we are testing AFTER we set up the patches.
# So we will do it inside setUp.

class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        """
        Set up a new KnowledgeBase instance for each test.
        This method now manually starts and stops the necessary patches
        with the CORRECT patch targets.
        """
        print("Setting up for a KnowledgeBase test")

        # --- CORRECTED PATCH TARGETS ---
        # We patch the names as they are looked up inside the 'knowledge_base.py' module.
        self.patcher_configure = patch('knowledge_base.genai.configure')
        self.patcher_embeddings = patch('knowledge_base.GoogleGenerativeAIEmbeddings')
        self.patcher_chroma = patch('knowledge_base.Chroma')
        self.patcher_splitter = patch('knowledge_base.RecursiveCharacterTextSplitter')

        # Start the patchers and get the mock objects
        self.MockConfigure = self.patcher_configure.start()
        self.MockEmbeddings = self.patcher_embeddings.start()
        self.MockChroma = self.patcher_chroma.start()
        self.MockSplitter = self.patcher_splitter.start()

        # Ensure the patchers are stopped after the test runs
        self.addCleanup(self.patcher_configure.stop)
        self.addCleanup(self.patcher_embeddings.stop)
        self.addCleanup(self.patcher_chroma.stop)
        self.addCleanup(self.patcher_splitter.stop)
       
        # Configure the return value of the Chroma() call itself
        self.mock_vector_store_instance = MagicMock()
        self.MockChroma.return_value = self.mock_vector_store_instance

        # Configure the text splitter to return predictable chunks
        self.MockSplitter.return_value.split_text.return_value = ['chunk1', 'chunk2']
       
        # Now that mocks are active, we can import and initialize KnowledgeBase
        from knowledge_base import KnowledgeBase
        self.kb = KnowledgeBase()

    def test_add_documents(self):
        """Tests if the add_documents method correctly calls the vector store."""
        print("Running test: test_add_documents")
        documents = ["This is the first document."]
        self.kb.add_documents(documents)
       
        # Assert that the method on our MOCK INSTANCE was called
        self.mock_vector_store_instance.add_texts.assert_called_with(texts=['chunk1', 'chunk2'])

    def test_query(self):
        """Tests if the query method correctly calls similarity_search."""
        print("Running test: test_query")
        # Define what our mock search should return
        mock_doc = MagicMock()
        mock_doc.page_content = "relevant chunk of text"
        self.mock_vector_store_instance.similarity_search.return_value = [mock_doc]
       
        results = self.kb.query("A question")
       
        # Check that the similarity_search method was called
        self.mock_vector_store_instance.similarity_search.assert_called_with("A question")
        self.assertEqual(results, ["relevant chunk of text"])

if __name__ == '__main__':
    unittest.main()