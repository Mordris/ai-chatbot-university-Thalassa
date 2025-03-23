import requests
from langdetect import detect, DetectorFactory

MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"

# Ensure consistent language detection results
DetectorFactory.seed = 0  

def detect_language(text):
    """Detects the language of the input text."""
    try:
        detected_lang = detect(text)
        return detected_lang  # Returns "tr" for Turkish, "en" for English, etc.
    except:
        return "en"  # Default to English if detection fails

def translate_text(text, source_lang, target_lang):
    """Translate the text from source_lang to target_lang."""
    try:
        response = requests.get(MYMEMORY_API_URL, params={
            "q": text,
            "langpair": f"{source_lang}|{target_lang}"
        })

        if response.status_code == 200:
            translated_text = response.json().get("responseData", {}).get("translatedText", "")
            return translated_text
        else:
            return text  # If translation fails, return original text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text on error

def translate_to_english(text):
    """Translate text to English and return the detected language."""
    detected_lang = detect_language(text)
    
    if detected_lang == "en":  # If already English, return as is
        return text, "en"
    
    try:
        return translate_text(text, "tr", "en"), "tr"  # Translate Turkish to English
    except Exception as e:
        print(f"Error during translation to English: {e}")
        return text, "en"  # Return original text if translation fails

def translate_to_turkish(text):
    """Translate text to Turkish."""
    try:
        return translate_text(text, "en", "tr")  # Translate English to Turkish
    except Exception as e:
        print(f"Error during translation to Turkish: {e}")
        return text  # Return original text if translation fails
