
import os
import logging
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

logger = logging.getLogger(__name__)

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    logger.error("GOOGLE_API_KEY environment variable not set.")
    exit()


class KnowledgeBase:
    def __init__(self):
        self.persist_directory = 'chroma_db'
       
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
       
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )
        logger.info(f"Knowledge base initialized. Loading from: {self.persist_directory}")


    def add_documents(self, documents: list[str]):
        """
        Takes a list of document texts, splits them into chunks,
        and adds them to the persistent Chroma vector store.
        """
        if not documents:
            logger.warning("No documents provided to add to the knowledge base.")
            return

        text_chunks = self.text_splitter.split_text("\n\n---\n\n".join(documents))

        if not text_chunks:
            logger.warning("No text chunks generated from the provided documents.")
            return

        logger.info(f"Adding {len(text_chunks)} text chunks to the Chroma vector store.")

        try:
            self.vector_store.add_texts(texts=text_chunks)
            logger.info("Successfully added new documents to the Chroma vector store.")
        except Exception as e:
            logger.error(f"An error occurred while adding documents to Chroma: {e}")

    def query(self, user_question: str) -> list[str]:
        """
        Performs a similarity search on the vector store to find relevant chunks.
        """
        if not self.vector_store:
            return []

        relevant_docs = self.vector_store.similarity_search(user_question)
        return [doc.page_content for doc in relevant_docs]
