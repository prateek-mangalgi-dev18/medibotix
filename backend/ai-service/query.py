# import os
# import re
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
#     Convert recent conversation messages into a compact
#     text representation.
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
# # PARSE LANGUAGE + REWRITTEN QUERY
# # ============================================================

# def parse_rewrite_response(response_text, fallback_question):
#     """
#     Parse the structured response:

#         LANGUAGE: English
#         QUERY: What is my hemoglobin level?
#     """

#     language = "English"
#     rewritten_query = fallback_question.strip()

#     try:

#         language_match = re.search(
#             r"LANGUAGE\s*:\s*(.+)",
#             response_text,
#             re.IGNORECASE
#         )

#         query_match = re.search(
#             r"QUERY\s*:\s*(.+)",
#             response_text,
#             re.IGNORECASE
#         )

#         if language_match:

#             detected_language = (
#                 language_match
#                 .group(1)
#                 .strip()
#             )

#             if detected_language:

#                 language = detected_language

#         if query_match:

#             detected_query = (
#                 query_match
#                 .group(1)
#                 .strip()
#             )

#             if detected_query:

#                 rewritten_query = detected_query

#     except Exception as e:

#         print(
#             f"Failed to parse rewrite response: {e}"
#         )

#     return language, rewritten_query


# # ============================================================
# # MULTILINGUAL CONTEXTUAL QUERY REWRITING
# # ============================================================

# def rewrite_query(question, history):
#     """
#     Detect the language of the CURRENT USER QUESTION and
#     convert the question into a standalone English retrieval
#     query.

#     Returns:

#         language
#         rewritten_query
#     """

#     history_text = format_history(
#         history
#     )

#     rewrite_prompt = f"""
# You are a multilingual query rewriting component inside
# Medibotix, a medical document RAG system.

# You have TWO tasks.

# TASK 1:
# Detect the language of the CURRENT USER QUESTION.

# TASK 2:
# Convert the CURRENT USER QUESTION into a standalone
# ENGLISH retrieval query.

# ------------------------------------------------------------

# IMPORTANT LANGUAGE RULE

# Detect the language ONLY from the CURRENT USER QUESTION.

# Do NOT use:

# - conversation history
# - uploaded document language
# - previous assistant messages

# to determine the response language.

# For example:

# CURRENT USER QUESTION:
# "What is my hemoglobin?"

# LANGUAGE: English

# Even if the conversation history contains Hindi.

# ------------------------------------------------------------

# CONVERSATION CONTEXT

# You may use conversation history ONLY to resolve references.

# Examples:

# - it
# - this
# - that
# - these
# - those
# - my results
# - my report
# - is it normal
# - am I safe
# - what about this

# Do NOT use history to determine the user's current language.

# ------------------------------------------------------------

# MEDICAL TERM PRESERVATION

# Never replace one medical parameter with another.

# These are different:

# - Hemoglobin ≠ HbA1c
# - WBC ≠ RBC
# - Hemoglobin ≠ Hematocrit
# - Glucose ≠ HbA1c
# - MCV ≠ MCH
# - MCH ≠ MCHC

# Example:

# Current question:

# "What is my hemoglobin?"

# Correct retrieval query:

# "What is my hemoglobin level?"

# Incorrect:

# "What is my HbA1c level?"

# Only use HbA1c when the user explicitly asks about HbA1c.

# ------------------------------------------------------------

# MULTILINGUAL RETRIEVAL

# If the user asks in another language:

# 1. Detect the language.
# 2. Understand the meaning.
# 3. Use history only if required to resolve context.
# 4. Convert the question into English.

# Example:

# Current question:

# "मेरा हीमोग्लोबिन कितना है?"

# Output:

# LANGUAGE: Hindi
# QUERY: What is my hemoglobin level?

# ------------------------------------------------------------

# FOLLOW-UP EXAMPLE

# Conversation history:

# User: What is my hemoglobin?
# Medibotix: Your hemoglobin is 14.4 g/dL.

# Current question:

# "क्या यह सामान्य है?"

# Output:

# LANGUAGE: Hindi
# QUERY: Is my hemoglobin level normal?

# ------------------------------------------------------------

# OUTPUT FORMAT

# Return EXACTLY:

# LANGUAGE: <detected language>
# QUERY: <standalone English retrieval query>

# Do not add explanations.

# ------------------------------------------------------------

# Conversation history:

# ---------------- HISTORY ----------------

# {history_text if history_text else "No previous conversation."}

# -------------- END HISTORY --------------


# CURRENT USER QUESTION:

# {question}
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

#         response_text = (
#             response
#             .choices[0]
#             .message
#             .content
#             .strip()
#         )

#         language, rewritten_query = (
#             parse_rewrite_response(
#                 response_text,
#                 question
#             )
#         )

#         return language, rewritten_query

#     except Exception as e:

#         print(
#             f"Query rewriting failed: {e}"
#         )

#     return "English", question.strip()


# # ============================================================
# # RETRIEVE DOCUMENT CONTEXT
# # ============================================================

# def retrieve_context(query, index, docs):
#     """
#     Generate an embedding for the English rewritten query
#     and retrieve relevant chunks from FAISS.
#     """

#     if not docs:

#         return ""

#     query_embedding = client.embeddings.create(
#         model="mistral-embed",
#         inputs=[query]
#     ).data[0].embedding

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
#     document_context,
#     response_language
# ):
#     """
#     Generate a grounded answer using:

#         Conversation history
#         +
#         Retrieved document context
#         +
#         Original question

#     The answer language is explicitly controlled using
#     response_language.
#     """

#     history_text = format_history(
#         history
#     )

#     system_prompt = f"""
# You are Medibotix, a medical document assistant.

# Your job is to help users understand their uploaded
# medical documents.

# ------------------------------------------------------------

# RESPONSE LANGUAGE

# You MUST answer ONLY in this language:

# {response_language}

# This language has already been detected from the CURRENT
# USER QUESTION.

# Do NOT choose another language.

# Do NOT change the answer language based on:

# - conversation history
# - uploaded document
# - previous assistant responses

# If RESPONSE LANGUAGE is English, answer completely in English.

# If RESPONSE LANGUAGE is Hindi, answer in Hindi.

# If RESPONSE LANGUAGE is Kannada, answer in Kannada.

# Follow the specified response language strictly.

# ------------------------------------------------------------

# DOCUMENT GROUNDING

# Use the retrieved uploaded document context as the primary
# source of factual information.

# Do not invent:

# - laboratory values
# - diagnoses
# - symptoms
# - findings
# - medical history

# Do not confuse medical tests.

# IMPORTANT:

# Hemoglobin and HbA1c are DIFFERENT tests.

# WBC and RBC are DIFFERENT tests.

# Never substitute one medical parameter for another.

# If the user asks for hemoglobin but the document context
# does not contain a confirmed hemoglobin result, do NOT give
# an HbA1c result instead.

# Clearly state that the requested result could not be found
# or confirmed from the uploaded document.

# ------------------------------------------------------------

# CONVERSATION CONTEXT

# Use conversation history to understand follow-up questions.

# Example:

# User:
# "What is my hemoglobin?"

# Medibotix:
# "Your hemoglobin is 14.4 g/dL."

# User:
# "Is it normal?"

# The user is asking whether the previously discussed
# hemoglobin result is normal.

# ------------------------------------------------------------

# MEDICAL SAFETY

# Do not make unsupported diagnoses.

# Do not tell the user they are definitely:

# - safe
# - healthy
# - cured
# - fine
# - not at risk

# unless the document explicitly supports that conclusion.

# When appropriate, explain that interpretation may depend on
# clinical context and consultation with a healthcare
# professional.

# ------------------------------------------------------------

# VALID QUESTIONS

# Questions about:

# - medical reports
# - laboratory values
# - hemoglobin
# - WBC
# - RBC
# - HbA1c
# - glucose
# - cholesterol
# - medicines
# - symptoms
# - uploaded images
# - uploaded documents

# are valid.

# Do NOT reject valid medical questions.

# ------------------------------------------------------------

# UNRELATED QUESTIONS

# Reject only questions that are clearly unrelated to:

# - health
# - medicine
# - the uploaded document

# If the question is unrelated, respond in the REQUIRED
# RESPONSE LANGUAGE with the equivalent meaning of:

# "I'm a medical assistant and can only help with
# health-related questions from your uploaded documents.
# Please ask me about your medical reports or health concerns."

# ------------------------------------------------------------

# ANSWER STYLE

# - Answer the user's actual question.
# - Be concise.
# - Use simple language.
# - Explain medical terms briefly when necessary.
# - Do not dump the entire document unless requested.
# - Preserve exact numbers and measurement units.
# """

#     user_prompt = f"""
# REQUIRED RESPONSE LANGUAGE:

# {response_language}


# RECENT CONVERSATION:

# ---------------- HISTORY ----------------

# {history_text if history_text else "No previous conversation."}

# -------------- END HISTORY --------------


# RETRIEVAL QUERY:

# {rewritten_query}


# RELEVANT UPLOADED DOCUMENT CONTEXT:

# ---------------- DOCUMENT ----------------

# {document_context}

# -------------- END DOCUMENT --------------


# CURRENT USER QUESTION:

# {question}


# Answer the CURRENT USER QUESTION.

# IMPORTANT:

# - Answer ONLY in {response_language}.
# - Use the document as the factual source.
# - Use history only to understand follow-up context.
# - Do not confuse different medical tests.
# - Do not replace hemoglobin with HbA1c.
# - Do not invent medical information.
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
#     Multilingual conversational RAG pipeline:

#         User Question
#               ↓
#         Language Detection
#               +
#         Contextual Query Rewriting
#               ↓
#         English Retrieval Query
#               ↓
#         Mistral Embedding
#               ↓
#         FAISS Retrieval
#               ↓
#         Retrieved Document Context
#               ↓
#         Answer Generation
#               ↓
#         Answer in Detected User Language
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
#     # 3. Detect language and rewrite query
#     # --------------------------------------------------------

#     response_language, rewritten_query = (
#         rewrite_query(
#             question,
#             history
#         )
#     )

#     print(
#         f"Original query: {question}"
#     )

#     print(
#         f"Detected language: {response_language}"
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
#         document_context=document_context,
#         response_language=response_language
#     )

#     return answer

import os
import re
import faiss
import pickle
import numpy as np

import time
from mistralai import Mistral
from mistralai.models.sdkerror import SDKError

from config import MISTRAL_API_KEY, MISTRAL_CHAT_MODEL


# ============================================================
# CONFIGURATION
# ============================================================

INDEX_FILE = "index.faiss"
DOCS_FILE = "docs.pkl"

# Number of recent messages retained for conversational context.
MAX_HISTORY_MESSAGES = 6


# ------------------------------------------------------------
# RETRIEVAL CONFIGURATION
# ------------------------------------------------------------

# Number of initial candidates retrieved from FAISS.
FAISS_CANDIDATE_K = 10

# Minimum cosine similarity required for a candidate chunk.
RELEVANCE_THRESHOLD = 0.30

# Number of final chunks selected after MMR.
FINAL_TOP_K = 4

# MMR balance:
#
# 1.0 = maximum relevance, no diversity consideration
# 0.0 = maximum diversity, little relevance consideration
#
# 0.7 gives stronger importance to relevance while still
# reducing redundant chunks.
MMR_LAMBDA = 0.70


client = Mistral(
    api_key=MISTRAL_API_KEY
)


# ============================================================
# MISTRAL API RETRY HELPER
# ============================================================

def call_mistral_with_retry(api_func, max_retries=4, initial_delay=1.5):
    """
    Executes a Mistral API call with exponential backoff on HTTP 429 rate limits.
    """
    for attempt in range(max_retries):
        try:
            return api_func()
        except SDKError as e:
            error_message = str(e)
            if "429" in error_message or "rate_limited" in error_message.lower():
                if attempt < max_retries - 1:
                    wait_time = initial_delay * (2 ** attempt)
                    print(
                        f"Rate limit hit (429). Retrying in {wait_time:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait_time)
                    continue
            raise
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "rate_limited" in error_message.lower():
                if attempt < max_retries - 1:
                    wait_time = initial_delay * (2 ** attempt)
                    print(
                        f"Rate limit hit (429). Retrying in {wait_time:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait_time)
                    continue
            raise


# ============================================================
# GREETING DETECTION
# ============================================================

GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|hola|namaste|howdy|sup)[\s!.,?]*$",
    r"^(good\s+(morning|afternoon|evening|day))[\s!.,?]*$",
    r"^(who\s+are\s+you|what\s+can\s+you\s+do)[\s!.,?]*$",
    r"^(help|can\s+you\s+help\s+me)[\s!.,?]*$"
]

def is_greeting(text: str) -> bool:
    cleaned = text.strip().lower()
    return any(re.match(p, cleaned) for p in GREETING_PATTERNS)


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

def parse_rewrite_response(
    response_text,
    fallback_question
):
    """
    Parse the structured response:

        LANGUAGE: English
        QUERY: What is my hemoglobin level?
    """

    language = "English"

    rewritten_query = (
        fallback_question.strip()
    )

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

                rewritten_query = (
                    detected_query
                )

    except Exception as e:

        print(
            f"Failed to parse rewrite response: {e}"
        )

    return (
        language,
        rewritten_query
    )


# ============================================================
# MULTILINGUAL CONTEXTUAL QUERY REWRITING
# ============================================================

def rewrite_query(
    question,
    history
):
    """
    Detect the language of the CURRENT USER QUESTION and
    convert the question into a standalone English retrieval
    query.

    Returns:

        language
        rewritten_query
    """

    # If there is no conversation history and the question is already in English,
    # we can bypass the extra LLM call to save latency and avoid rate limits.
    if not history and question.isascii():
        return (
            "English",
            question.strip()
        )

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

        def _do_rewrite():
            return client.chat.complete(
                model=MISTRAL_CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": rewrite_prompt
                    }
                ]
            )

        response = call_mistral_with_retry(
            _do_rewrite,
            max_retries=3,
            initial_delay=1.5
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

        return (
            language,
            rewritten_query
        )

    except Exception as e:

        print(
            f"Query rewriting failed: {e}"
        )

    return (
        "English",
        question.strip()
    )


# ============================================================
# VECTOR NORMALIZATION
# ============================================================

def normalize_vector(
    vector
):
    """
    Normalize a vector to unit length.

    This allows dot products between vectors to represent
    cosine similarity.
    """

    vector = np.array(
        vector,
        dtype="float32"
    )

    norm = np.linalg.norm(
        vector
    )

    if norm == 0:

        return vector

    return vector / norm


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    vector_a,
    vector_b
):
    """
    Calculate cosine similarity between two vectors.
    """

    vector_a = normalize_vector(
        vector_a
    )

    vector_b = normalize_vector(
        vector_b
    )

    return float(
        np.dot(
            vector_a,
            vector_b
        )
    )


# ============================================================
# GET FAISS VECTOR
# ============================================================

def get_index_vector(
    index,
    vector_id
):
    """
    Retrieve the stored embedding vector from FAISS.

    The returned vector is later used for:

        - cosine relevance calculation
        - MMR diversity calculation
    """

    try:

        vector = index.reconstruct(
            int(vector_id)
        )

        return np.array(
            vector,
            dtype="float32"
        )

    except Exception as e:

        print(
            f"Failed to reconstruct vector "
            f"{vector_id}: {e}"
        )

        return None


# ============================================================
# RELEVANCE FILTERING
# ============================================================

def filter_relevant_candidates(
    query_vector,
    candidate_vectors,
    candidate_indices
):
    """
    Filter FAISS candidates based on cosine similarity.

    Returns a list of dictionaries containing:

        {
            "index": document index,
            "vector": embedding,
            "relevance": cosine similarity
        }
    """

    relevant_candidates = []

    for candidate_index, candidate_vector in zip(
        candidate_indices,
        candidate_vectors
    ):

        relevance_score = cosine_similarity(
            query_vector,
            candidate_vector
        )

        if relevance_score >= RELEVANCE_THRESHOLD:

            relevant_candidates.append(
                {
                    "index": int(
                        candidate_index
                    ),
                    "vector": candidate_vector,
                    "relevance": relevance_score
                }
            )

    return relevant_candidates


# ============================================================
# MAXIMAL MARGINAL RELEVANCE
# ============================================================

def apply_mmr(
    query_vector,
    candidates,
    top_k=FINAL_TOP_K,
    lambda_value=MMR_LAMBDA
):
    """
    Select relevant but diverse chunks using
    Maximal Marginal Relevance.

    Formula:

        MMR =
            lambda × relevance_to_query
            -
            (1 - lambda) × redundancy

    Where:

        relevance_to_query
            = similarity between query and candidate

        redundancy
            = maximum similarity between the candidate
              and already selected chunks
    """

    if not candidates:

        return []

    selected_candidates = []

    remaining_candidates = candidates.copy()

    while (
        remaining_candidates
        and len(selected_candidates) < top_k
    ):

        best_candidate = None

        best_mmr_score = -float(
            "inf"
        )

        for candidate in remaining_candidates:

            relevance = candidate[
                "relevance"
            ]

            # ------------------------------------------------
            # First selection
            #
            # No selected chunks exist yet, so redundancy is 0.
            # ------------------------------------------------

            if not selected_candidates:

                redundancy = 0.0

            else:

                redundancy_scores = []

                for selected in selected_candidates:

                    similarity = cosine_similarity(
                        candidate["vector"],
                        selected["vector"]
                    )

                    redundancy_scores.append(
                        similarity
                    )

                redundancy = max(
                    redundancy_scores
                )

            mmr_score = (
                lambda_value
                * relevance
                -
                (1 - lambda_value)
                * redundancy
            )

            candidate[
                "mmr_score"
            ] = mmr_score

            if mmr_score > best_mmr_score:

                best_mmr_score = mmr_score

                best_candidate = candidate

        if best_candidate is None:

            break

        selected_candidates.append(
            best_candidate
        )

        remaining_candidates.remove(
            best_candidate
        )

    return selected_candidates


# ============================================================
# RETRIEVE DOCUMENT CONTEXT
# ============================================================

def retrieve_context(
    query,
    index,
    docs
):
    """
    Retrieval pipeline:

        Query
          ↓
        Mistral Embedding
          ↓
        FAISS Candidate Retrieval
          ↓
        Cosine Relevance Filtering
          ↓
        MMR Re-ranking
          ↓
        Diverse + Relevant Chunks
    """

    if not docs:

        return ""

    # --------------------------------------------------------
    # 1. Generate query embedding
    # --------------------------------------------------------

    def _do_embed():
        return (
            client
            .embeddings
            .create(
                model="mistral-embed",
                inputs=[query]
            )
            .data[0]
            .embedding
        )

    query_embedding = call_mistral_with_retry(
        _do_embed,
        max_retries=3,
        initial_delay=1.0
    )

    query_vector = normalize_vector(
        query_embedding
    )

    # --------------------------------------------------------
    # 2. Retrieve larger candidate pool from FAISS
    # --------------------------------------------------------

    candidate_k = min(
        FAISS_CANDIDATE_K,
        len(docs)
    )

    distances, indices = index.search(
        np.array(
            [query_embedding]
        ).astype(
            "float32"
        ),
        candidate_k
    )

    candidate_indices = []

    candidate_vectors = []

    # --------------------------------------------------------
    # 3. Reconstruct candidate vectors
    #
    # We use the stored FAISS embeddings for cosine relevance
    # filtering and MMR diversity calculation.
    # --------------------------------------------------------

    for idx in indices[0]:

        if idx < 0:

            continue

        if idx >= len(docs):

            continue

        candidate_vector = get_index_vector(
            index,
            idx
        )

        if candidate_vector is None:

            continue

        candidate_indices.append(
            idx
        )

        candidate_vectors.append(
            candidate_vector
        )

    if not candidate_indices:

        return ""

    # --------------------------------------------------------
    # 4. Relevance filtering
    # --------------------------------------------------------

    relevant_candidates = (
        filter_relevant_candidates(
            query_vector,
            candidate_vectors,
            candidate_indices
        )
    )

    # --------------------------------------------------------
    # Fallback
    #
    # If the threshold removes every candidate, we do not
    # immediately return an empty result.
    #
    # Instead, keep the best FAISS candidates so the system
    # remains robust for short or unusual medical queries.
    # --------------------------------------------------------

    if not relevant_candidates:

        print(
            "No candidates passed relevance threshold."
        )

        print(
            "Using FAISS candidates as fallback."
        )

        for candidate_index, candidate_vector in zip(
            candidate_indices,
            candidate_vectors
        ):

            relevance_score = cosine_similarity(
                query_vector,
                candidate_vector
            )

            relevant_candidates.append(
                {
                    "index": int(
                        candidate_index
                    ),
                    "vector": candidate_vector,
                    "relevance": relevance_score
                }
            )

    # --------------------------------------------------------
    # Sort by relevance before MMR
    # --------------------------------------------------------

    relevant_candidates.sort(
        key=lambda candidate: (
            candidate["relevance"]
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # 5. Apply MMR
    # --------------------------------------------------------

    selected_candidates = apply_mmr(
        query_vector=query_vector,
        candidates=relevant_candidates,
        top_k=min(
            FINAL_TOP_K,
            len(relevant_candidates)
        ),
        lambda_value=MMR_LAMBDA
    )

    if not selected_candidates:

        return ""

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    print(
        "\nRetrieval optimization:"
    )

    print(
        f"  FAISS candidates: "
        f"{len(candidate_indices)}"
    )

    print(
        f"  After relevance filtering: "
        f"{len(relevant_candidates)}"
    )

    print(
        f"  Final MMR chunks: "
        f"{len(selected_candidates)}"
    )

    for position, candidate in enumerate(
        selected_candidates,
        start=1
    ):

        print(
            f"  Chunk {position}: "
            f"index={candidate['index']}, "
            f"relevance="
            f"{candidate['relevance']:.4f}, "
            f"MMR="
            f"{candidate.get('mmr_score', 0):.4f}"
        )

    # --------------------------------------------------------
    # 6. Convert selected chunks into document context
    # --------------------------------------------------------

    retrieved_chunks = []

    for candidate in selected_candidates:

        document_index = candidate[
            "index"
        ]

        if (
            document_index >= 0
            and document_index < len(docs)
        ):

            retrieved_chunks.append(
                docs[
                    document_index
                ]
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

    def _do_generate():
        return client.chat.complete(
            model=MISTRAL_CHAT_MODEL,
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

    response = call_mistral_with_retry(
        _do_generate,
        max_retries=4,
        initial_delay=1.5
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
    Optimized multilingual conversational RAG pipeline:

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
        FAISS Candidate Retrieval
              ↓
        Relevance Filtering
              ↓
        MMR Re-ranking
              ↓
        Diverse Relevant Context
              ↓
        Grounded Answer Generation
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
    # 2. Validate question & handle greetings
    # --------------------------------------------------------

    question = question.strip()

    if not question:

        return (
            "Please enter a question about "
            "your uploaded document."
        )

    if is_greeting(question):

        return (
            "Hello! I am **Medibotix**, your AI assistant for medical documents. "
            "I have analyzed your uploaded health report. "
            "How can I assist you with your report or test results today?"
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
        f"Detected language: "
        f"{response_language}"
    )

    print(
        f"Rewritten query: "
        f"{rewritten_query}"
    )

    # --------------------------------------------------------
    # 4. Retrieve optimized document context
    #
    # FAISS
    #     ↓
    # Relevance filtering
    #     ↓
    # MMR
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