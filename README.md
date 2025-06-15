# ai-chatbot

A Flask-based AI chatbot application that can process uploaded documents (PDF, TXT) and Google Document links to build a knowledge base. It uses a Large Language Model (LLM) to answer user queries based on this knowledge base and can also fetch information from web URLs provided in the chat.

## Features

*   **Document Upload:** Supports uploading `.txt` and `.pdf` files to build a knowledge base.
*   **Google Docs Integration:** Can process publicly readable Google Document links to add to the knowledge base.
*   **URL Scraping:** If a URL is detected in the user's query, the chatbot can scrape the content of the URL to inform its response.
*   **URL Shortening:** Shortens any URLs present in the AI's responses.
*   **Chat Interface:** A simple web interface for interacting with the chatbot.
*   **Conversation History:** Remembers the last 3 pairs of user/AI messages (6 total messages) to maintain context.
*   **Vector Store:** Uses ChromaDB to store and query document embeddings for efficient information retrieval.

## Tech Stack

*   **Backend:** Python, Flask
*   **LLM Integration:** Langchain, Google Generative AI (Gemini)
*   **Vector Database:** ChromaDB
*   **Web Scraping:** BeautifulSoup, Selenium
*   **File Processing:** PyPDF2
*   **Frontend:** HTML, CSS, JavaScript

## Project Structure

```
ai-chatbot/
├── server/
│   ├── app.py                # Main Flask application, API endpoints
│   ├── knowledge_base.py     # Handles ChromaDB interactions
│   ├── tools.py              # Utility functions (file processing, URL scraping, etc.)
│   ├── requirements.txt      # Python dependencies
│   ├── chromedriver          # Selenium WebDriver for Chrome
│   ├── chroma_db/            # Directory for ChromaDB data
│   ├── static/               # Frontend files (HTML, CSS, JS)
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   ├── tests/                # Unit tests
│   │   ├── test_app.py
│   │   ├── test_knowledge_base.py
│   │   └── test_tools.py
│   └── uploads/              # Default folder for uploaded files
└── README.md                 # This file
```

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/Mahika14/ai-chatbot
    cd ai-chatbot
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Python dependencies:**
    Navigate to the `server` directory and install the required packages.
    ```bash
    cd server
    pip install -r requirements.txt
    ```
4.  **Google API Key:**
    Ensure you have a Google API key for the Gemini LLM. Set this as an environment variable.
    export GOOGLE_API_KEY=<your api key>

5.  **Download ChromeDriver:**
    *   Determine the version of Google Chrome installed on your system.
    *   Download the corresponding ChromeDriver executable from the [official ChromeDriver website](https://chromedriver.chromium.org/downloads).
    *   Place the `chromedriver` executable in the `ai-chatbot/server/` directory.
    *   Ensure the `chromedriver` is executable:
        ```bash
        chmod +x server/chromedriver
        ```

## Running the Application

1.  **Navigate to the `server` directory:**
    ```bash
    cd server
    ```
2.  **Run the Flask application:**
    ```bash
    python app.py
    ```
3.  Open your web browser and go to `http://127.0.0.1:5000/` (or the address shown in your terminal).

## API Endpoints

*   `GET /`: Serves the main chat interface.
*   `POST /upload`: Handles file uploads (PDF, TXT) and Google Doc links to update the knowledge base.
*   `POST /chat`: Receives user queries and returns AI-generated responses.

## How to Use

1.  Start the application as described above.
2.  Open the web interface in your browser.
3.  To build the knowledge base:
    *   Click the paperclip icon (📎) to select `.txt` or `.pdf` files.
    *   Alternatively, paste a Google Document link directly into the chat input along with your query or as a standalone message.
    *   The system will process these and update the knowledge base.
4.  Ask questions in the chat input. If your question relates to the uploaded documents or provided links, the AI will use that information.
5.  If you include a URL in your query, the AI will attempt to fetch information from that webpage.

## How to Run the unit tests?

```bash
     python -m unittest discover tests
```


