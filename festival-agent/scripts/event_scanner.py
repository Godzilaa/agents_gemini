import sys
from google import genai
from google.genai import types

def run_scanner(query):
    client = genai.Client()
    # Tool definition for search grounding
    search_tool = types.Tool(google_search=types.GoogleSearch())
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=query,
        config=types.GenerateContentConfig(tools=[search_tool])
    )
    print(response.text)

if __name__ == "__main__":
    location = sys.argv[1] if len(sys.argv) > 1 else "Bengaluru"
    run_scanner(f"events near {location}")
