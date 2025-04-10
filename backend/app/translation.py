# app/translation.py
import requests
from langdetect import detect, LangDetectException, DetectorFactory
import os
import logging

# Configuration
MYMEMORY_API_URL = os.getenv("MYMEMORY_API_URL", "https://api.mymemory.translated.net/get")

# Ensure consistent language detection results
try:
    DetectorFactory.seed = 0
except Exception as e:
     logging.warning(f"Could not set DetectorFactory seed: {e}") # Handle potential issues if library changes

def detect_language(text):
    """Detects the language of the input text."""
    if not text or not isinstance(text, str) or text.isspace():
        return "en" # Default to English for empty or invalid input
    try:
        # Add confidence check if needed, but keep simple for now
        detected_lang = detect(text)
        # Filter for common expected languages if necessary
        # supported_langs = ["en", "tr"]
        # return detected_lang if detected_lang in supported_langs else "en"
        return detected_lang
    except LangDetectException:
        logging.warning(f"Language detection failed for text (first 50 chars): '{text[:50]}...'. Defaulting to English.")
        return "en"  # Default to English if detection fails

def translate_text(text, source_lang, target_lang):
    """Translate the text from source_lang to target_lang using MyMemory."""
    if not text or not isinstance(text, str) or text.isspace():
        return text # Return original if input is invalid

    # Avoid translating if source and target are the same
    if source_lang == target_lang:
        return text

    lang_pair = f"{source_lang}|{target_lang}"
    params = {"q": text, "langpair": lang_pair}
    headers = {'User-Agent': 'ThalassaAI/1.0'} # Add a User-Agent

    logging.info(f"Translating '{text[:50]}...' from {source_lang} to {target_lang}")

    try:
        response = requests.get(MYMEMORY_API_URL, params=params, headers=headers, timeout=10) # Add timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        translated_text = data.get("responseData", {}).get("translatedText")
        match_quality = data.get("responseStatus") # Check status code

        if response.status_code == 200 and match_quality == 200 and translated_text:
             # Basic check for common MyMemory error messages sometimes returned in text
            if "INVALID LANGUAGE PAIR" in translated_text or \
               "PLEASE SPECIFY SOURCETEXT" in translated_text or \
               "QUERY LENGTH LIMIT EXCEDEED" in translated_text:
                logging.warning(f"MyMemory translation returned an error message: {translated_text}")
                return text # Return original text
            logging.info(f"Translation successful: '{translated_text[:50]}...'")
            return translated_text
        else:
             logging.warning(f"Translation failed or returned unexpected data. Status: {match_quality}, Data: {data}")
             return text # Return original text if translation fails

    except requests.exceptions.Timeout:
         logging.error(f"Translation request timed out for lang pair {lang_pair}.")
         return text
    except requests.exceptions.RequestException as e:
        logging.error(f"Translation HTTP error ({lang_pair}): {e}")
        return text  # Return original text on connection error
    except Exception as e:
        logging.error(f"General translation error ({lang_pair}): {e}", exc_info=True)
        return text  # Return original text on other errors

def translate_to_english(text):
    """Translate text to English, returning translated text and original language."""
    original_lang = detect_language(text)
    logging.info(f"Detected language for translation to English: {original_lang}")

    if original_lang == "en":
        return text, "en" # Return original text and 'en' language code

    # Assuming other detected languages should be translated (e.g., Turkish 'tr')
    translated_text = translate_text(text, original_lang, "en")
    return translated_text, original_lang # Return translated text and original language detected

# Note: We don't strictly need translate_to_turkish anymore if OpenAI handles the response language.
# But it can be kept for potential future use or debugging.
def translate_to_turkish(text):
    """Translate text from English to Turkish."""
    return translate_text(text, "en", "tr")