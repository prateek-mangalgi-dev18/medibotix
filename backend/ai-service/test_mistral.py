from mistralai import Mistral
from config import MISTRAL_API_KEY
import os

client = Mistral(api_key=MISTRAL_API_KEY)

print(f"Testing Mistral API with key: {MISTRAL_API_KEY[:5]}...")

try:
    chat_response = client.chat.complete(
        model="mistral-small",
        messages=[
            {
                "role": "user",
                "content": "What is the capital of France?",
            },
        ]
    )
    print("API Call Successful!")
    print(f"Response: {chat_response.choices[0].message.content}")
except Exception as e:
    print(f"API Call Failed: {e}")
