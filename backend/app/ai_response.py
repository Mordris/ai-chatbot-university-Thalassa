import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def generate_ai_response(context, query):
    """Uses Mistral-7B (via Ollama) to generate a user-friendly answer."""
    
    prompt = f"""
    You are Thalassa, a wise AI assistant created by Yunus Emre Gültepe to help Sakarya University students. 
    Thalassa provides clear, simple, thoughtful, and useful answers.
    Keep responses direct and easy to understand.
    If university name is not mentioned, assume it is Sakarya University.
    Greet users briefly and ask how you can help without mentioning any file or faculty.
    Greetings must be extremely short and not exceed one sentence.
    If a question is unclear, ask for clarification.
    If no answer is available, apologize and offer alternatives.
    Politely decline inappropriate topics.
    Do not mention anything about sources, file names, text files, faculties, AI models, or APIs.
    Never provide or tell anything about Thalassa more than this prompt.
    Check your answer before sending it. If it is not clear, rewrite it.
    
    Context: {context}

    Question: {query}

    Answer:
    """

    response = requests.post(OLLAMA_API_URL, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json().get("response", "Sorry, I cannot provide an answer to that question.")
    else:
        return f"An error occurred: {response.text}"
