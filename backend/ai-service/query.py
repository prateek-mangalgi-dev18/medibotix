# import os
# import faiss
# import pickle
# import numpy as np

# from mistralai import Mistral

# from config import MISTRAL_API_KEY


# # ============================================================
# # CONFIGURATION
# # ============================================================

# INDEX_FILE = "index.faiss"
# DOCS_FILE = "docs.pkl"

# # Number of previous messages used for conversational context.
# # We intentionally keep this bounded to prevent the context
# # from growing indefinitely.
# MAX_HISTORY_MESSAGES = 6


# client = Mistral(
#     api_key=MISTRAL_API_KEY
# )


# # ============================================================
# # LOAD FAISS INDEX
# # ============================================================

# def load_index():
#     """
#     Load the FAISS index and stored document chunks.
#     """

#     if (
#         not os.path.exists(INDEX_FILE)
#         or not os.path.exists(DOCS_FILE)
#     ):
#         return None, None

#     try:

#         index = faiss.read_index(
#             INDEX_FILE
#         )

#         with open(
#             DOCS_FILE,
#             "rb"
#         ) as f:

#             docs = pickle.load(f)

#         return index, docs

#     except Exception as e:

#         print(
#             f"Failed to load FAISS index: {e}"
#         )

#         return None, None


# # ============================================================
# # FORMAT CONVERSATION HISTORY
# # ============================================================

# def format_history(history):
#     """
#     Convert recent conversation messages into a
#     compact text representation.

#     Only the latest MAX_HISTORY_MESSAGES messages
#     are retained.
#     """

#     if not history:
#         return ""

#     recent_history = history[
#         -MAX_HISTORY_MESSAGES:
#     ]

#     formatted_messages = []

#     for message in recent_history:

#         role = message.get(
#             "role",
#             ""
#         )

#         content = message.get(
#             "content",
#             ""
#         )

#         if not content:
#             continue

#         if role == "user":

#             formatted_messages.append(
#                 f"User: {content}"
#             )

#         elif role == "assistant":

#             formatted_messages.append(
#                 f"Medibotix: {content}"
#             )

#     return "\n".join(
#         formatted_messages
#     )


# # ============================================================
# # CONTEXTUAL QUERY REWRITING
# # ============================================================

# def rewrite_query(question, history):
#     """
#     Convert a conversational/follow-up question into
#     a standalone retrieval query.

#     Example:

#         Previous:
#         User: What does the image say?
#         Medibotix: Your blood test shows...

#         Current:
#         "Am I safe?"

#     Becomes something similar to:

#         "Based on the uploaded blood test report,
#         are there any findings that may indicate
#         a health concern?"
#     """

#     history_text = format_history(
#         history
#     )

#     # --------------------------------------------------------
#     # No conversation history
#     # --------------------------------------------------------

#     if not history_text:

#         return question.strip()

#     rewrite_prompt = f"""
# You are a query rewriting component inside Medibotix,
# a medical document RAG system.

# Your task is to rewrite the user's CURRENT QUESTION
# into a standalone retrieval query that can be used
# to search the uploaded medical document.

# Use the conversation history to resolve references such as:

# - it
# - this
# - that
# - these
# - those
# - my results
# - my report
# - the image
# - the result
# - is that normal
# - am I safe
# - what about this
# - what does that mean

# IMPORTANT RULES:

# 1. Preserve the user's original intent.

# 2. Resolve vague references using the conversation.

# 3. Do NOT answer the question.

# 4. Do NOT add medical facts that are not present
#    in the conversation.

# 5. Do NOT diagnose the patient.

# 6. The output must be a single standalone question
#    suitable for semantic retrieval.

# 7. If the current question is already standalone,
#    return it with minimal or no modification.

# Conversation history:

# ---------------- HISTORY ----------------

# {history_text}

# -------------- END HISTORY --------------

# Current question:

# {question}

# Return ONLY the rewritten standalone question.
# """

#     try:

#         response = client.chat.complete(
#             model="mistral-small",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": rewrite_prompt
#                 }
#             ]
#         )

#         rewritten = (
#             response
#             .choices[0]
#             .message
#             .content
#             .strip()
#         )

#         if rewritten:

#             return rewritten

#     except Exception as e:

#         print(
#             f"Query rewriting failed: {e}"
#         )

#     # --------------------------------------------------------
#     # Fallback
#     # --------------------------------------------------------

#     return question.strip()


# # ============================================================
# # RETRIEVE DOCUMENT CONTEXT
# # ============================================================

# def retrieve_context(query, index, docs):
#     """
#     Generate an embedding for the query and retrieve
#     the most relevant document chunks from FAISS.
#     """

#     if not docs:

#         return ""

#     # --------------------------------------------------------
#     # Embed rewritten query
#     # --------------------------------------------------------

#     query_embedding = client.embeddings.create(
#         model="mistral-embed",
#         inputs=[query]
#     ).data[0].embedding

#     # --------------------------------------------------------
#     # Retrieve a few candidates
#     #
#     # We keep this at 5 for now.
#     #
#     # Later, when we implement MMR + reranking,
#     # this will become a larger candidate set.
#     # --------------------------------------------------------

#     top_k = min(
#         5,
#         len(docs)
#     )

#     distances, indices = index.search(
#         np.array(
#             [query_embedding]
#         ).astype("float32"),
#         top_k
#     )

#     retrieved_chunks = []

#     for idx in indices[0]:

#         if idx < 0:
#             continue

#         if idx >= len(docs):
#             continue

#         retrieved_chunks.append(
#             docs[idx]
#         )

#     return "\n\n".join(
#         retrieved_chunks
#     )


# # ============================================================
# # FINAL ANSWER GENERATION
# # ============================================================

# def generate_answer(
#     question,
#     rewritten_query,
#     history,
#     document_context
# ):
#     """
#     Generate the final grounded answer using:

#         Recent conversation
#         +
#         Retrieved document context
#         +
#         Current question
#     """

#     history_text = format_history(
#         history
#     )

#     system_prompt = """
# You are Medibotix, a medical document assistant.

# Your job is to help the user understand their uploaded
# medical documents and the health information contained
# within them.

# IMPORTANT RULES:

# 1. CONVERSATION CONTEXT

# The user may ask follow-up questions.

# Use the recent conversation context to understand what
# the user is referring to.

# For example:

# User:
# "What does the image say?"

# Medibotix:
# "The report shows..."

# User:
# "Am I safe?"

# The second question refers to the previously discussed
# medical report.

# Do not treat a follow-up question as an unrelated
# question simply because it is short or vague.

# ------------------------------------------------------------

# 2. DOCUMENT GROUNDING

# Use the retrieved medical document context as the
# primary factual source.

# Do not invent values, diagnoses, symptoms, or findings
# that are not supported by the uploaded document.

# If the requested information cannot be found in the
# retrieved context, clearly say that the information could
# not be found in the uploaded document.

# ------------------------------------------------------------

# 3. MEDICAL SAFETY

# Do not make unsupported diagnoses.

# Do not tell the user that they are definitely:

# - safe
# - healthy
# - cured
# - fine
# - not at risk
# - not concerning

# unless that conclusion is explicitly supported by
# the document.

# A medical report alone may not be enough to determine
# whether a person is medically "safe".

# When appropriate, explain what the report shows and
# state that proper interpretation depends on clinical
# context and should be discussed with a qualified
# healthcare professional.

# ------------------------------------------------------------

# 4. DOCUMENT QUESTIONS ARE VALID

# Questions such as:

# - What does the image say?
# - What does the report say?
# - What is written in the document?
# - Can you read this?
# - Summarize the report.
# - What are my results?
# - What does this result mean?

# are valid questions when a document has been uploaded.

# ------------------------------------------------------------

# 5. SIMPLE LANGUAGE

# Use simple language that a person without medical
# training can understand.

# If a medical term is necessary, explain it briefly.

# ------------------------------------------------------------

# 6. ANSWER THE ACTUAL QUESTION

# Be concise and directly answer what the user asked.

# Do not dump the entire document unless the user asks
# for a complete summary.

# ------------------------------------------------------------

# 7. UNRELATED QUESTIONS

# If the question is completely unrelated to the uploaded
# medical document or health, respond exactly with:

# "I'm a medical assistant and can only help with health-related questions from your uploaded documents. Please ask me about your medical reports or health concerns."

# ------------------------------------------------------------

# 8. IMPORTANT

# The rewritten query is ONLY used for document retrieval.

# Answer the user's ORIGINAL question, not the rewritten
# retrieval query.
# """

#     user_prompt = f"""
# RECENT CONVERSATION:

# ---------------- HISTORY ----------------

# {history_text if history_text else "No previous conversation."}

# -------------- END HISTORY --------------


# RETRIEVAL QUERY USED:

# {rewritten_query}


# RELEVANT UPLOADED DOCUMENT CONTEXT:

# ---------------- DOCUMENT ----------------

# {document_context}

# -------------- END DOCUMENT --------------


# CURRENT USER QUESTION:

# {question}


# Answer the CURRENT USER QUESTION using the conversation
# and uploaded document context.

# Remember:

# - Use the conversation to resolve follow-up questions.
# - Use the document as the factual source.
# - Do not invent medical information.
# - Do not give unsupported medical reassurance.
# - Do not answer the rewritten retrieval query instead of
#   the user's original question.
# """

#     response = client.chat.complete(
#         model="mistral-small",
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 "role": "user",
#                 "content": user_prompt
#             }
#         ]
#     )

#     return (
#         response
#         .choices[0]
#         .message
#         .content
#     )


# # ============================================================
# # MAIN QUESTION PIPELINE
# # ============================================================

# def ask_question(
#     question,
#     history=None
# ):
#     """
#     Conversational RAG pipeline:

#         Question
#             ↓
#         Recent history
#             ↓
#         Query rewriting
#             ↓
#         Mistral embedding
#             ↓
#         FAISS retrieval
#             ↓
#         Document context
#             +
#         Conversation context
#             ↓
#         Mistral answer
#     """

#     if history is None:

#         history = []

#     # --------------------------------------------------------
#     # 1. Load FAISS
#     # --------------------------------------------------------

#     index, docs = load_index()

#     if index is None:

#         return (
#             "No documents uploaded yet. "
#             "Please upload a file first."
#         )

#     # --------------------------------------------------------
#     # 2. Validate question
#     # --------------------------------------------------------

#     question = question.strip()

#     if not question:

#         return (
#             "Please enter a question about "
#             "your uploaded document."
#         )

#     # --------------------------------------------------------
#     # 3. Rewrite conversational query
#     # --------------------------------------------------------

#     rewritten_query = rewrite_query(
#         question,
#         history
#     )

#     print(
#         f"Original query: {question}"
#     )

#     print(
#         f"Rewritten query: {rewritten_query}"
#     )

#     # --------------------------------------------------------
#     # 4. Retrieve document context
#     # --------------------------------------------------------

#     document_context = retrieve_context(
#         rewritten_query,
#         index,
#         docs
#     )

#     if not document_context:

#         return (
#             "I could not find relevant information "
#             "in the uploaded document."
#         )

#     # --------------------------------------------------------
#     # 5. Generate final answer
#     # --------------------------------------------------------

#     answer = generate_answer(
#         question=question,
#         rewritten_query=rewritten_query,
#         history=history,
#         document_context=document_context
#     )

#     return answer

import os
import re
import faiss
import pickle
import numpy as np

from mistralai import Mistral

from config import MISTRAL_API_KEY


# ============================================================
# CONFIGURATION
# ============================================================

INDEX_FILE = "index.faiss"
DOCS_FILE = "docs.pkl"

MAX_HISTORY_MESSAGES = 6


client = Mistral(
    api_key=MISTRAL_API_KEY
)


# ============================================================
# LOAD FAISS INDEX
# ============================================================

def load_index():
    """
    Load the FAISS index and stored document chunks.
    """

    if (
        not os.path.exists(INDEX_FILE)
        or not os.path.exists(DOCS_FILE)
    ):
        return None, None

    try:

        index = faiss.read_index(
            INDEX_FILE
        )

        with open(
            DOCS_FILE,
            "rb"
        ) as f:

            docs = pickle.load(f)

        return index, docs

    except Exception as e:

        print(
            f"Failed to load FAISS index: {e}"
        )

        return None, None


# ============================================================
# FORMAT CONVERSATION HISTORY
# ============================================================

def format_history(history):
    """
    Convert recent conversation messages into a compact
    text representation.
    """

    if not history:
        return ""

    recent_history = history[
        -MAX_HISTORY_MESSAGES:
    ]

    formatted_messages = []

    for message in recent_history:

        role = message.get(
            "role",
            ""
        )

        content = message.get(
            "content",
            ""
        )

        if not content:
            continue

        if role == "user":

            formatted_messages.append(
                f"User: {content}"
            )

        elif role == "assistant":

            formatted_messages.append(
                f"Medibotix: {content}"
            )

    return "\n".join(
        formatted_messages
    )


# ============================================================
# PARSE LANGUAGE + REWRITTEN QUERY
# ============================================================

def parse_rewrite_response(response_text, fallback_question):
    """
    Parse the structured response:

        LANGUAGE: English
        QUERY: What is my hemoglobin level?
    """

    language = "English"
    rewritten_query = fallback_question.strip()

    try:

        language_match = re.search(
            r"LANGUAGE\s*:\s*(.+)",
            response_text,
            re.IGNORECASE
        )

        query_match = re.search(
            r"QUERY\s*:\s*(.+)",
            response_text,
            re.IGNORECASE
        )

        if language_match:

            detected_language = (
                language_match
                .group(1)
                .strip()
            )

            if detected_language:

                language = detected_language

        if query_match:

            detected_query = (
                query_match
                .group(1)
                .strip()
            )

            if detected_query:

                rewritten_query = detected_query

    except Exception as e:

        print(
            f"Failed to parse rewrite response: {e}"
        )

    return language, rewritten_query


# ============================================================
# MULTILINGUAL CONTEXTUAL QUERY REWRITING
# ============================================================

def rewrite_query(question, history):
    """
    Detect the language of the CURRENT USER QUESTION and
    convert the question into a standalone English retrieval
    query.

    Returns:

        language
        rewritten_query
    """

    history_text = format_history(
        history
    )

    rewrite_prompt = f"""
You are a multilingual query rewriting component inside
Medibotix, a medical document RAG system.

You have TWO tasks.

TASK 1:
Detect the language of the CURRENT USER QUESTION.

TASK 2:
Convert the CURRENT USER QUESTION into a standalone
ENGLISH retrieval query.

------------------------------------------------------------

IMPORTANT LANGUAGE RULE

Detect the language ONLY from the CURRENT USER QUESTION.

Do NOT use:

- conversation history
- uploaded document language
- previous assistant messages

to determine the response language.

For example:

CURRENT USER QUESTION:
"What is my hemoglobin?"

LANGUAGE: English

Even if the conversation history contains Hindi.

------------------------------------------------------------

CONVERSATION CONTEXT

You may use conversation history ONLY to resolve references.

Examples:

- it
- this
- that
- these
- those
- my results
- my report
- is it normal
- am I safe
- what about this

Do NOT use history to determine the user's current language.

------------------------------------------------------------

MEDICAL TERM PRESERVATION

Never replace one medical parameter with another.

These are different:

- Hemoglobin ≠ HbA1c
- WBC ≠ RBC
- Hemoglobin ≠ Hematocrit
- Glucose ≠ HbA1c
- MCV ≠ MCH
- MCH ≠ MCHC

Example:

Current question:

"What is my hemoglobin?"

Correct retrieval query:

"What is my hemoglobin level?"

Incorrect:

"What is my HbA1c level?"

Only use HbA1c when the user explicitly asks about HbA1c.

------------------------------------------------------------

MULTILINGUAL RETRIEVAL

If the user asks in another language:

1. Detect the language.
2. Understand the meaning.
3. Use history only if required to resolve context.
4. Convert the question into English.

Example:

Current question:

"मेरा हीमोग्लोबिन कितना है?"

Output:

LANGUAGE: Hindi
QUERY: What is my hemoglobin level?

------------------------------------------------------------

FOLLOW-UP EXAMPLE

Conversation history:

User: What is my hemoglobin?
Medibotix: Your hemoglobin is 14.4 g/dL.

Current question:

"क्या यह सामान्य है?"

Output:

LANGUAGE: Hindi
QUERY: Is my hemoglobin level normal?

------------------------------------------------------------

OUTPUT FORMAT

Return EXACTLY:

LANGUAGE: <detected language>
QUERY: <standalone English retrieval query>

Do not add explanations.

------------------------------------------------------------

Conversation history:

---------------- HISTORY ----------------

{history_text if history_text else "No previous conversation."}

-------------- END HISTORY --------------


CURRENT USER QUESTION:

{question}
"""

    try:

        response = client.chat.complete(
            model="mistral-small",
            messages=[
                {
                    "role": "system",
                    "content": rewrite_prompt
                }
            ]
        )

        response_text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        language, rewritten_query = (
            parse_rewrite_response(
                response_text,
                question
            )
        )

        return language, rewritten_query

    except Exception as e:

        print(
            f"Query rewriting failed: {e}"
        )

    return "English", question.strip()


# ============================================================
# RETRIEVE DOCUMENT CONTEXT
# ============================================================

def retrieve_context(query, index, docs):
    """
    Generate an embedding for the English rewritten query
    and retrieve relevant chunks from FAISS.
    """

    if not docs:

        return ""

    query_embedding = client.embeddings.create(
        model="mistral-embed",
        inputs=[query]
    ).data[0].embedding

    top_k = min(
        5,
        len(docs)
    )

    distances, indices = index.search(
        np.array(
            [query_embedding]
        ).astype("float32"),
        top_k
    )

    retrieved_chunks = []

    for idx in indices[0]:

        if idx < 0:
            continue

        if idx >= len(docs):
            continue

        retrieved_chunks.append(
            docs[idx]
        )

    return "\n\n".join(
        retrieved_chunks
    )


# ============================================================
# FINAL ANSWER GENERATION
# ============================================================

def generate_answer(
    question,
    rewritten_query,
    history,
    document_context,
    response_language
):
    """
    Generate a grounded answer using:

        Conversation history
        +
        Retrieved document context
        +
        Original question

    The answer language is explicitly controlled using
    response_language.
    """

    history_text = format_history(
        history
    )

    system_prompt = f"""
You are Medibotix, a medical document assistant.

Your job is to help users understand their uploaded
medical documents.

------------------------------------------------------------

RESPONSE LANGUAGE

You MUST answer ONLY in this language:

{response_language}

This language has already been detected from the CURRENT
USER QUESTION.

Do NOT choose another language.

Do NOT change the answer language based on:

- conversation history
- uploaded document
- previous assistant responses

If RESPONSE LANGUAGE is English, answer completely in English.

If RESPONSE LANGUAGE is Hindi, answer in Hindi.

If RESPONSE LANGUAGE is Kannada, answer in Kannada.

Follow the specified response language strictly.

------------------------------------------------------------

DOCUMENT GROUNDING

Use the retrieved uploaded document context as the primary
source of factual information.

Do not invent:

- laboratory values
- diagnoses
- symptoms
- findings
- medical history

Do not confuse medical tests.

IMPORTANT:

Hemoglobin and HbA1c are DIFFERENT tests.

WBC and RBC are DIFFERENT tests.

Never substitute one medical parameter for another.

If the user asks for hemoglobin but the document context
does not contain a confirmed hemoglobin result, do NOT give
an HbA1c result instead.

Clearly state that the requested result could not be found
or confirmed from the uploaded document.

------------------------------------------------------------

CONVERSATION CONTEXT

Use conversation history to understand follow-up questions.

Example:

User:
"What is my hemoglobin?"

Medibotix:
"Your hemoglobin is 14.4 g/dL."

User:
"Is it normal?"

The user is asking whether the previously discussed
hemoglobin result is normal.

------------------------------------------------------------

MEDICAL SAFETY

Do not make unsupported diagnoses.

Do not tell the user they are definitely:

- safe
- healthy
- cured
- fine
- not at risk

unless the document explicitly supports that conclusion.

When appropriate, explain that interpretation may depend on
clinical context and consultation with a healthcare
professional.

------------------------------------------------------------

VALID QUESTIONS

Questions about:

- medical reports
- laboratory values
- hemoglobin
- WBC
- RBC
- HbA1c
- glucose
- cholesterol
- medicines
- symptoms
- uploaded images
- uploaded documents

are valid.

Do NOT reject valid medical questions.

------------------------------------------------------------

UNRELATED QUESTIONS

Reject only questions that are clearly unrelated to:

- health
- medicine
- the uploaded document

If the question is unrelated, respond in the REQUIRED
RESPONSE LANGUAGE with the equivalent meaning of:

"I'm a medical assistant and can only help with
health-related questions from your uploaded documents.
Please ask me about your medical reports or health concerns."

------------------------------------------------------------

ANSWER STYLE

- Answer the user's actual question.
- Be concise.
- Use simple language.
- Explain medical terms briefly when necessary.
- Do not dump the entire document unless requested.
- Preserve exact numbers and measurement units.
"""

    user_prompt = f"""
REQUIRED RESPONSE LANGUAGE:

{response_language}


RECENT CONVERSATION:

---------------- HISTORY ----------------

{history_text if history_text else "No previous conversation."}

-------------- END HISTORY --------------


RETRIEVAL QUERY:

{rewritten_query}


RELEVANT UPLOADED DOCUMENT CONTEXT:

---------------- DOCUMENT ----------------

{document_context}

-------------- END DOCUMENT --------------


CURRENT USER QUESTION:

{question}


Answer the CURRENT USER QUESTION.

IMPORTANT:

- Answer ONLY in {response_language}.
- Use the document as the factual source.
- Use history only to understand follow-up context.
- Do not confuse different medical tests.
- Do not replace hemoglobin with HbA1c.
- Do not invent medical information.
"""

    response = client.chat.complete(
        model="mistral-small",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return (
        response
        .choices[0]
        .message
        .content
    )


# ============================================================
# MAIN QUESTION PIPELINE
# ============================================================

def ask_question(
    question,
    history=None
):
    """
    Multilingual conversational RAG pipeline:

        User Question
              ↓
        Language Detection
              +
        Contextual Query Rewriting
              ↓
        English Retrieval Query
              ↓
        Mistral Embedding
              ↓
        FAISS Retrieval
              ↓
        Retrieved Document Context
              ↓
        Answer Generation
              ↓
        Answer in Detected User Language
    """

    if history is None:

        history = []

    # --------------------------------------------------------
    # 1. Load FAISS
    # --------------------------------------------------------

    index, docs = load_index()

    if index is None:

        return (
            "No documents uploaded yet. "
            "Please upload a file first."
        )

    # --------------------------------------------------------
    # 2. Validate question
    # --------------------------------------------------------

    question = question.strip()

    if not question:

        return (
            "Please enter a question about "
            "your uploaded document."
        )

    # --------------------------------------------------------
    # 3. Detect language and rewrite query
    # --------------------------------------------------------

    response_language, rewritten_query = (
        rewrite_query(
            question,
            history
        )
    )

    print(
        f"Original query: {question}"
    )

    print(
        f"Detected language: {response_language}"
    )

    print(
        f"Rewritten query: {rewritten_query}"
    )

    # --------------------------------------------------------
    # 4. Retrieve document context
    # --------------------------------------------------------

    document_context = retrieve_context(
        rewritten_query,
        index,
        docs
    )

    if not document_context:

        return (
            "I could not find relevant information "
            "in the uploaded document."
        )

    # --------------------------------------------------------
    # 5. Generate final answer
    # --------------------------------------------------------

    answer = generate_answer(
        question=question,
        rewritten_query=rewritten_query,
        history=history,
        document_context=document_context,
        response_language=response_language
    )

    return answer