import os
import faiss
import pickle
import numpy as np
from mistralai import Mistral
from config import MISTRAL_API_KEY

INDEX_FILE = "index.faiss"
DOCS_FILE = "docs.pkl"

client = Mistral(api_key=MISTRAL_API_KEY)

def load_index():
    if not os.path.exists(INDEX_FILE) or not os.path.exists(DOCS_FILE):
        return None, None

    index = faiss.read_index(INDEX_FILE)
    try:
        with open(DOCS_FILE, "rb") as f:
            docs = pickle.load(f)
        return index, docs
    except Exception:
        return None, None



def ask_question(q):
    index, docs = load_index()

    if index is None:
        return "No documents uploaded yet. Please upload a file first."

    q_emb = client.embeddings.create(
        model="mistral-embed",
        inputs=[q]
    ).data[0].embedding

    D, I = index.search(
        np.array([q_emb]).astype("float32"), 3
    )

    context = " ".join([docs[i] for i in I[0]])

    chat = client.chat.complete(
        model="mistral-small",
        messages=[
            {
              "role": "system",
              "content": """You are a medical AI assistant helping patients understand their medical reports and health information.

IMPORTANT RULES:
1. ONLY answer questions related to medical reports, health, symptoms, or medical conditions found in the uploaded document
2. If asked about non-medical topics (politics, sports, general knowledge, current events, etc.), respond EXACTLY with: "I'm a medical assistant and can only help with health-related questions from your uploaded documents. Please ask me about your medical reports or health concerns."
3. Use SIMPLE language that anyone can understand - imagine explaining to someone with no medical education
4. Be CONCISE - only answer what is directly asked, don't provide extra information unless necessary
5. Do NOT mention: test costs, laboratory names, technical test methods, billing information, or administrative details
6. Focus on: what the results mean for health, what they indicate, and simple explanations
7. Avoid medical jargon - use everyday words
8. If technical terms are necessary, explain them in simple terms

Your goal is to help patients understand their health in clear, simple language."""
            },
            {
              "role": "user",
              "content": f"Based on this medical document:\n\n{context}\n\nQuestion: {q}\n\nProvide a simple, clear answer."
            }
        ]
    )

    return chat.choices[0].message.content
