from fastapi import FastAPI, UploadFile
from ingest import ingest_file
from query import ask_question
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


app = FastAPI()
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(file: UploadFile):
    try:
        logging.info(f"Receiving upload: {file.filename}")
        content = await file.read()
        logging.info(f"File size: {len(content)} bytes")
        
        ingest_file(file.filename, content)
        
        logging.info(f"Successfully processed: {file.filename}")
        return {"message": "uploaded", "filename": file.filename}
    except Exception as e:
        error_message = str(e)
        logging.error(f"Upload failed for {file.filename}: {error_message}")
        
        # Return a user-friendly error message
        return {
            "error": error_message,
            "message": f"Failed to process file: {error_message}"
        }

from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: QueryRequest):
    try:
        logging.info(f"Query received: {request.question}")
        answer = ask_question(request.question)
        return {"answer": answer}
    except Exception as e:
        error_message = str(e)
        logging.error(f"Query failed: {error_message}")
        return {
            "error": error_message,
            "message": f"Failed to get answer: {error_message}"
        }

