import faiss
import pickle
import numpy as np
import time
import io
from mistralai import Mistral
from mistralai.models.sdkerror import SDKError
from pypdf import PdfReader
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

INDEX_FILE = "index.faiss"
DOCS_FILE = "docs.pkl"

def embed_batch(texts, max_retries=3):
    """
    Embed multiple texts in a single API call with retry logic.
    
    Args:
        texts: List of text strings to embed
        max_retries: Maximum number of retry attempts for rate limit errors
    
    Returns:
        List of embedding vectors
    """
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(
                model="mistral-embed",
                inputs=texts
            )
            return [item.embedding for item in response.data]
        except SDKError as e:
            # Check if it's a rate limit error (status 429)
            if "429" in str(e) or "rate_limited" in str(e).lower():
                if attempt < max_retries - 1:
                    # Exponential backoff: wait 2^attempt seconds
                    wait_time = 2 ** attempt
                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    raise Exception(f"Rate limit exceeded after {max_retries} attempts. Please try again in a few moments.")
            else:
                # Not a rate limit error, re-raise
                raise


def extract_text_from_file(filename, content):
    """
    Extract text from various file formats.
    
    Args:
        filename: Name of the file (used to determine type)
        content: File content as bytes
    
    Returns:
        Extracted text as string
    """
    # Check file extension
    if filename.lower().endswith('.pdf'):
        # Extract text from PDF
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("PDF appears to be empty or contains no extractable text")
            
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    else:
        # Plain text file
        return content.decode(errors="ignore")


def ingest_file(filename, content):
    """
    Process and index a file for semantic search.
    
    Args:
        filename: Name of the uploaded file
        content: File content as bytes
    """
    # Extract text from file (handles PDF and text files)
    text = extract_text_from_file(filename, content)

    # Split into overlapping chunks
    chunks = [
        text[i:i+500]
        for i in range(0, len(text), 450)
    ]
    
    if not chunks:
        chunks = [text] if text.strip() else ["No extractable text found in this document."]

    # Batch embed all chunks in a single API call
    vectors = embed_batch(chunks)
    
    if not vectors:
        raise ValueError("Failed to generate embeddings for the document.")

    # Create FAISS index
    dim = len(vectors[0])

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))

    # Save index and documents
    faiss.write_index(index, INDEX_FILE)
    with open(DOCS_FILE, "wb") as f:
        pickle.dump(chunks, f)
