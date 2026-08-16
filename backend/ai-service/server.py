from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import logging

from ingest import ingest_file
from query import ask_question


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# UPLOAD
# ============================================================

@app.post("/upload")
async def upload(file: UploadFile):

    try:

        logging.info(
            f"Receiving upload: {file.filename}"
        )

        content = await file.read()

        logging.info(
            f"File size: {len(content)} bytes"
        )

        ingest_file(
            file.filename,
            content
        )

        logging.info(
            f"Successfully processed: {file.filename}"
        )

        return {
            "message": "uploaded",
            "filename": file.filename
        }

    except Exception as e:

        error_message = str(e)

        logging.error(
            f"Upload failed for "
            f"{file.filename}: {error_message}"
        )

        return {
            "error": error_message,
            "message": (
                f"Failed to process file: "
                f"{error_message}"
            )
        }


# ============================================================
# CHAT MESSAGE MODEL
# ============================================================

class ChatMessage(BaseModel):

    role: Literal[
        "user",
        "assistant"
    ]

    content: str


# ============================================================
# QUERY REQUEST
# ============================================================

class QueryRequest(BaseModel):

    question: str

    history: List[ChatMessage] = []


# ============================================================
# ASK
# ============================================================

@app.post("/ask")
async def ask(request: QueryRequest):

    try:

        logging.info(
            f"Query received: "
            f"{request.question}"
        )

        # Convert Pydantic models into dictionaries
        history = [
            {
                "role": message.role,
                "content": message.content
            }
            for message in request.history
        ]

        logging.info(
            f"Conversation messages received: "
            f"{len(history)}"
        )

        answer = ask_question(
            question=request.question,
            history=history
        )

        return {
            "answer": answer
        }

    except Exception as e:

        error_message = str(e)

        logging.error(
            f"Query failed: {error_message}"
        )

        return {
            "error": error_message,
            "message": (
                f"Failed to get answer: "
                f"{error_message}"
            )
        }