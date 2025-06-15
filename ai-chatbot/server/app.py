import os
import re
import logging
from flask import Flask, request, jsonify, send_from_directory
from tools import url_scraper_tool, file_processor_tool, url_shortener_tool, find_and_clean_urls
from knowledge_base import KnowledgeBase
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

logger = logging.getLogger(__name__)

app = Flask(__name__)
kb = KnowledgeBase()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- Route to serve the frontend UI ---
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# --- Route to upload documents and build the knowledge base ---
@app.route('/upload', methods=['POST'])
def upload_files():
    """
    Handles knowledge base creation. It saves all inputs to the 'uploads' folder,
    then processes them to extract text and build/add to the knowledge base.
    """
    files = request.files.getlist('files')
    gdoc_link = request.form.get('gdoc_link')

    if not files and not gdoc_link:
        return jsonify({"error": "No files or Google Doc link provided"}), 400
   
    if len(files) > 3:
        return jsonify({"error": "You can upload a maximum of 3 documents."}), 400
   
    all_text_content = []
   
    # Process file uploads
    for file in files:
        if file.filename == '':
            continue
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        with open(file_path, 'rb') as saved_file:
            original_content, scraped_content = file_processor_tool(saved_file, filename)
        if original_content: all_text_content.append(original_content)
        if scraped_content: all_text_content.append(scraped_content)
       
    # Process a Google Doc link if provided
    if gdoc_link:
        gdoc_content, _ = url_scraper_tool(gdoc_link, save_to_folder=app.config['UPLOAD_FOLDER'])
        if gdoc_content: all_text_content.append(gdoc_content)

    # Build/add to the Knowledge Base
    if not all_text_content:
        return jsonify({"error": "Could not extract any text from the provided sources."}), 400
   
    kb.add_documents(all_text_content)

    return jsonify({
        "message": "Successfully added documents to the knowledge base."
    }), 200


# --- Main route for chat functionality ---
@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat queries, now with conversation memory.
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Invalid request: 'query' field is required."}), 400

    user_query = data.get('query')
    history = data.get('history', [])

    # Truncate history to the last 3 conversation pairs (6 messages)
    if len(history) > 6:
        history = history[-6:]

    # Build the list of messages for the LLM
    messages = [
        SystemMessage(content="You are a helpful assistant. Answer questions based on the provided context.")
    ]
    for message in history:
        if message.get('role') == 'user':
            messages.append(HumanMessage(content=message.get('content')))
        elif message.get('role') == 'ai':
            messages.append(AIMessage(content=message.get('content')))

    # --- Router Logic ---
    found_urls = find_and_clean_urls(user_query)
    context = ""
   
    if found_urls:
        all_scraped_content = []
        for url in found_urls:
            scraped_content, _ = url_scraper_tool(url)
            all_scraped_content.append(scraped_content)
        context = "\n\n".join(all_scraped_content)
       
        url_pattern_for_sub = r'https?://\S+'
        question_text = re.sub(url_pattern_for_sub, "", user_query).strip()
        if not question_text:
            question_text = "Summarize the content of the provided web page(s)."
       
        final_user_prompt = f"Answer the following question based only on the provided web page content.\n\nWeb Page Content:\n{context}\n\nQuestion:\n{question_text}"

    else:
        if not kb.vector_store:
            return jsonify({"error": "Knowledge base is not yet built. Please use the /upload endpoint first."}), 400

        relevant_chunks = kb.query(user_query)
        if not relevant_chunks:
            context = "No relevant information found in the documents."
        else:
            context = "\n\n".join(relevant_chunks)
       
        final_user_prompt = f"""
        Answer the following question based only on the provided context.
        If the context does not contain the answer, say "I'm sorry, I couldn't find an answer in the provided documents."

        Context:
        {context}

        Question:
        {user_query}
        """

    messages.append(HumanMessage(content=final_user_prompt))

    # Invoke the LLM
    logger.info("Generating answer with conversation history...")
    llm_response = llm.invoke(messages)
    response_text = llm_response.content
   
    # Process for URL shortening
    final_response = url_shortener_tool(response_text)

    return jsonify({"response": final_response})


# --- Main execution block ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)