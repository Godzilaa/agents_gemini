import sys
from google import genai
from google.genai import types

def run_scanner(query):
    client = genai.Client()
    # Tool definition for search grounding
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    response = client.models.generate_content(
        model="gemini-3-flash",
        config=types.GenerateContentConfig(tools=[search_tool]),
        contents=f"Search for road closures or festivals in Bengaluru near: {query}"
    )
    print(response.text)

if __name__ == "__main__":
    # In Linux, we pass arguments from the shell
    location = sys.argv[1] if len(sys.argv) > 1 else "Bengaluru"
    run_scanner(location)
