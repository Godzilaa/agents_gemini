import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

def translate_advisory(text: str, target_lang: str) -> str:
    """
    Translate advisory text to target language using Gemini API.
    Returns original text if language is English or API not configured.
    """
    if target_lang.lower() in ["en", "english"]:
        return text
    
    if not model:
        return f"{text} (Translation Unavailable: API Key missing)"

    try:
        prompt = f"Translate the following transport advisory to {target_lang}. Keep it concise and professional.\n\nAdvisory: {text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation failed: {e}")
        return text
