import requests
from typing import Optional
from config import Config


def generate_content(prompt: str, model: str = "openai/gpt-oss-120b", temperature: float = 0.2, max_tokens: int = 512) -> str:
    """Call the Groq OpenAI-compatible chat completions endpoint and return the assistant text.

    Returns the assistant-generated text. Raises requests.HTTPError on failure.
    """
    url = Config.GROQ_API_URL
    api_key = Config.GROQ_API_KEY

    if not api_key:
        raise RuntimeError('GROQ_API_KEY is not set in configuration')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
        'model': model,
        'messages': [
            { 'role': 'system', 'content': 'You are a helpful assistant.' },
            { 'role': 'user', 'content': prompt }
        ],
        'temperature': temperature,
        'max_tokens': max_tokens
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        # include response text for easier debugging
        raise

    data = resp.json()

    # OpenAI-style response: choices[0].message.content
    if 'choices' in data and len(data['choices']) > 0:
        choice = data['choices'][0]
        # Newer APIs may include 'message' with 'content'
        if isinstance(choice, dict):
            message = choice.get('message') or choice.get('delta') or {}
            if isinstance(message, dict):
                text = message.get('content')
                if text:
                    return text
            # Fallback: some providers return 'text' field
            text = choice.get('text')
            if text:
                return text

    # Last-resort: try top-level 'text' or error
    if 'text' in data:
        return data['text']

    raise RuntimeError('Unexpected response format from LLM provider')
