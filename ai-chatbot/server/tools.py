import requests
import os 
import re 
import logging
import time
import PyPDF2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

logger = logging.getLogger(__name__)

def url_scraper_tool(url: str, save_to_folder: str = None) -> (str, str): # type: ignore
    """
    Intelligently scrapes a URL and optionally saves the content.

    Returns a tuple: (text_content, saved_file_path)
    - saved_file_path will be None if save_to_folder is not specified.
    """
    # --- Special Handler for Google Docs ---
    if 'docs.google.com' in url:
        try:
            logger.info(f"Detected Google Doc. Using direct export for: {url}")
            match = re.search(r'/document/d/([^/]+)', url)
            if not match:
                return "Error: Could not extract Google Doc ID from URL.", None
           
            doc_id = match.group(1)
            export_url = f'https://docs.google.com/document/d/{doc_id}/export?format=txt'
           
            response = requests.get(export_url, timeout=10)
            response.raise_for_status()
           
            content = response.text
            saved_path = None

            if save_to_folder:
                filename = f"gdoc_{doc_id}.txt"
                saved_path = os.path.join(save_to_folder, filename)
                with open(saved_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Saved Google Doc content to: {saved_path}")

            return content, saved_path

        except Exception as e:
            return f"Error: Could not export Google Doc. Details: {e}", None

    # --- Default Selenium Handler for all other websites ---
    else:
        content = ""
        try:
            logger.info(f"Using Selenium for general URL: {url}")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            time.sleep(3)
            page_source = driver.page_source
            driver.quit()
            soup = BeautifulSoup(page_source, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
           
            return content, None

        except Exception as e:
            return f"Error: Could not retrieve content using Selenium. Details: {e}", None

def process_urls_in_parallel(urls: list[str]) -> list[str]:
    """
    Scrapes a list of URLs in parallel using a thread pool.
    Returns a list of the scraped text content.
    """
    scraped_contents = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda url: url_scraper_tool(url)[0], urls)
       
        for content in results:
            scraped_contents.append(content)
           
    return scraped_contents

    
def file_processor_tool(file_stream, file_name: str) -> (str, str):
    """
    Reads content from a file stream (.txt or .pdf), extracts text,
    finds any URLs within the text, and scrapes them.

    Returns a tuple containing:
    1. The original text content from the file.
    2. The combined text content scraped from all URLs found in the file.
    """
    original_text = ""
    scraped_text = ""

    if file_name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file_stream)
        for page in pdf_reader.pages:
            original_text += page.extract_text() or ""
    elif file_name.endswith('.txt'):
        original_text = file_stream.read().decode('utf-8')
    else:
        return "", "Unsupported file type."

    found_urls = find_and_clean_urls(original_text)
   
    if found_urls:
        logger.info(f"Found {len(found_urls)} URLs in {file_name}. Scraping them now.")
        scraped_contents = process_urls_in_parallel(set(found_urls))
        scraped_text = "\n\n--- End of Scraped Content ---\n\n".join(scraped_contents)

    return original_text, scraped_text

def find_and_clean_urls(text: str) -> list[str]:
    """
    Finds all URLs in a text and cleans them by stripping common trailing punctuation.
    """
    url_pattern = r'https?://\S+'
    found_urls = re.findall(url_pattern, text)
   
    # List of common punctuation to strip from the end of a URL
    trailing_punctuation = '.,;:)!?'
   
    # Clean each URL by stripping the trailing characters
    cleaned_urls = [url.rstrip(trailing_punctuation) for url in found_urls]
   
    return cleaned_urls

def url_shortener_tool(text_content: str) -> str:
    """
    Finds all URLs in a string and replaces them with shortened versions from is.gd.
    """
    urls_to_shorten = find_and_clean_urls(text_content)

    for long_url in urls_to_shorten:
        if 'is.gd' in long_url:
            continue
        try:
            api_url = f"https://is.gd/create.php?format=simple&url={long_url}"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            short_url = response.text
            text_content = re.sub(re.escape(long_url) + r'[.,;:)!?]*', short_url, text_content, 1)
        except requests.exceptions.RequestException as e:
            logger.error(f"URL shortening failed for {long_url}. Error: {e}")
            continue
           
    return text_content
