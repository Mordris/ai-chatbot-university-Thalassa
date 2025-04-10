# translate_files.py
import os
import requests
import time
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Configuration ---
load_dotenv() # Load environment variables from .env

# Get folder paths from .env or use defaults
SOURCE_FOLDER = os.getenv("TURKISH_TEXT_FOLDER", "extracted_texts") # Folder with original Turkish files
TARGET_FOLDER = os.getenv("TEXT_FOLDER", "extracted_texts_en") # Folder for translated English files (must match .env for RAG)

# MyMemory API settings
MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"
# Add optional email for higher anonymous usage limits with MyMemory (replace if needed)
# See: https://mymemory.translated.net/doc/usagelimits.php
MYMEMORY_EMAIL = os.getenv("MYMEMORY_EMAIL", None)

# Rate limiting delay between requests (in seconds) to avoid API limits
# Increase if you get rate limit errors (e.g., 429 status code)
DELAY_SECONDS = float(os.getenv("TRANSLATION_DELAY", 1.5))

# Number of parallel translation threads (be cautious with high numbers due to API limits)
MAX_WORKERS = int(os.getenv("TRANSLATION_WORKERS", 2))

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')
# --- End Configuration ---


def translate_text_via_mymemory(text, source_lang="tr", target_lang="en"):
    """Translates text using the MyMemory API."""
    if not text or text.isspace():
        return ""

    lang_pair = f"{source_lang}|{target_lang}"
    params = {"q": text, "langpair": lang_pair}
    if MYMEMORY_EMAIL:
        params['de'] = MYMEMORY_EMAIL # Add email as 'de' parameter if provided

    headers = {'User-Agent': 'ThalassaFileTranslator/1.0'}
    translated_text = ""

    try:
        logging.debug(f"Requesting translation for text snippet: '{text[:50]}...'")
        response = requests.get(MYMEMORY_API_URL, params=params, headers=headers, timeout=30) # Increased timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Check MyMemory response status specifically
        response_status = data.get("responseStatus")
        if response_status == 200:
            translated_text = data.get("responseData", {}).get("translatedText", "")
            # Basic check for common errors sometimes returned in text
            if "INVALID LANGUAGE PAIR" in translated_text or \
               "QUERY LENGTH LIMIT EXCEDEED" in translated_text or \
               "PLEASE PROVIDE A TEXT TO TRANSLATE" in translated_text:
                logging.warning(f"MyMemory API returned an error message within translatedText: {translated_text}. Snippet: '{text[:50]}...'")
                return text # Return original on API error message
            logging.debug(f"Translation successful for snippet: '{text[:50]}...'")
        elif response_status == 429:
             logging.error(f"MyMemory Rate Limit (429) hit for text: '{text[:50]}...'. Consider increasing DELAY_SECONDS.")
             return text # Return original text on rate limit
        else:
            logging.warning(f"MyMemory translation failed or returned non-200 status ({response_status}) for text: '{text[:50]}...'. Data: {data}")
            return text # Return original text if translation fails

    except requests.exceptions.Timeout:
         logging.error(f"Translation request timed out for text: '{text[:50]}...'. Returning original.")
         return text
    except requests.exceptions.RequestException as e:
        logging.error(f"Translation HTTP error for text '{text[:50]}...': {e}")
        return text  # Return original text on connection error
    except Exception as e:
        logging.error(f"General translation error for text '{text[:50]}...': {e}", exc_info=True)
        return text  # Return original text on other errors

    return translated_text

def translate_single_file(filename):
    """Reads, translates, and writes a single file."""
    source_path = os.path.join(SOURCE_FOLDER, filename)
    target_path = os.path.join(TARGET_FOLDER, filename)

    # Skip if target file already exists (optional behavior)
    # if os.path.exists(target_path):
    #     logging.info(f"Skipping '{filename}', target file already exists.")
    #     return filename, True # Indicate skipped

    logging.info(f"Processing '{filename}'...")
    try:
        with open(source_path, 'r', encoding='utf-8') as infile:
            original_content = infile.read()

        if not original_content or original_content.isspace():
            logging.warning(f"Skipping empty file: '{filename}'")
            # Write an empty target file? Or just skip? Skipping for now.
            return filename, True # Indicate success (empty file handled)

        # --- Add delay *before* each API call ---
        logging.debug(f"Waiting {DELAY_SECONDS}s before translating '{filename}'...")
        time.sleep(DELAY_SECONDS)
        # --- End delay ---

        translated_content = translate_text_via_mymemory(original_content, source_lang="tr", target_lang="en")

        if translated_content == original_content:
             logging.warning(f"Translation may have failed for '{filename}' (returned original content).")
             # Decide whether to write the original or skip writing on failure. Writing original for now.

        # Write the translated (or original if failed) content
        with open(target_path, 'w', encoding='utf-8') as outfile:
            outfile.write(translated_content)

        logging.info(f"Finished processing '{filename}'. Output saved to '{target_path}'.")
        return filename, True # Indicate success

    except FileNotFoundError:
        logging.error(f"Source file not found: '{source_path}'. Skipping.")
        return filename, False
    except IOError as e:
        logging.error(f"I/O error processing file '{filename}': {e}")
        return filename, False
    except Exception as e:
        logging.error(f"Unexpected error processing file '{filename}': {e}", exc_info=True)
        return filename, False


def main():
    """Main function to orchestrate file translation."""
    logging.info("--- Starting File Translation Script ---")
    logging.info(f"Source Folder (Turkish): {SOURCE_FOLDER}")
    logging.info(f"Target Folder (English): {TARGET_FOLDER}")
    logging.info(f"Inter-request Delay: {DELAY_SECONDS} seconds")
    logging.info(f"Max Parallel Workers: {MAX_WORKERS}")
    if MYMEMORY_EMAIL:
        logging.info(f"Using MyMemory Email: {MYMEMORY_EMAIL}")
    else:
        logging.info("Not using specific MyMemory Email (lower anonymous limits may apply).")


    # Validate source folder exists
    if not os.path.isdir(SOURCE_FOLDER):
        logging.error(f"Source folder '{SOURCE_FOLDER}' not found. Exiting.")
        return

    # Create target folder if it doesn't exist
    try:
        os.makedirs(TARGET_FOLDER, exist_ok=True)
        logging.info(f"Ensured target folder '{TARGET_FOLDER}' exists.")
    except OSError as e:
        logging.error(f"Could not create target folder '{TARGET_FOLDER}': {e}. Exiting.")
        return

    # List source files
    try:
        files_to_translate = [f for f in os.listdir(SOURCE_FOLDER) if f.endswith('.txt')]
        if not files_to_translate:
            logging.warning(f"No .txt files found in '{SOURCE_FOLDER}'. Exiting.")
            return
        logging.info(f"Found {len(files_to_translate)} .txt files to translate.")
    except Exception as e:
        logging.error(f"Error listing files in source folder '{SOURCE_FOLDER}': {e}. Exiting.")
        return

    # Process files using a thread pool
    successful_translations = 0
    failed_translations = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix='Translator') as executor:
        futures = [executor.submit(translate_single_file, filename) for filename in files_to_translate]

        for future in as_completed(futures):
            try:
                filename, success = future.result()
                if success:
                    successful_translations += 1
                else:
                    failed_translations += 1
            except Exception as e:
                 # This shouldn't happen often if translate_single_file handles its errors
                 logging.error(f"Error retrieving result for a file translation task: {e}", exc_info=True)
                 failed_translations += 1

    end_time = time.time()
    total_time = end_time - start_time

    logging.info("--- Translation Process Complete ---")
    logging.info(f"Successfully processed: {successful_translations} files")
    logging.info(f"Failed/Skipped:       {failed_translations} files")
    logging.info(f"Total time taken:     {total_time:.2f} seconds")
    logging.warning("IMPORTANT: Please manually review the translated files in the target folder for accuracy.")

if __name__ == "__main__":
    main()