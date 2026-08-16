import base64
import io
import os
import pickle
import re
import time

import faiss
import numpy as np

from docx import Document
from mistralai import Mistral
from mistralai.models.sdkerror import SDKError
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from pypdf import PdfReader

from config import MISTRAL_API_KEY


# ============================================================
# CLIENT
# ============================================================

client = Mistral(
    api_key=MISTRAL_API_KEY
)


# ============================================================
# MISTRAL TOKENIZER
# ============================================================

tokenizer = MistralTokenizer.v3()


# ============================================================
# STORAGE
# ============================================================

INDEX_FILE = "index.faiss"
DOCS_FILE = "docs.pkl"


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".txt",
}


IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


# ============================================================
# CHUNKING CONFIGURATION
# ============================================================

# Preferred chunk size.
TARGET_CHUNK_TOKENS = 350

# Absolute maximum.
#
# NO final chunk is allowed to exceed this value.
MAX_CHUNK_TOKENS = 500

# We avoid semantic splitting when the current chunk is
# extremely small.
MIN_CHUNK_TOKENS = 100

# Context carried between adjacent chunks.
OVERLAP_TOKENS = 50

# API batching.
SENTENCE_EMBED_BATCH_SIZE = 32
CHUNK_EMBED_BATCH_SIZE = 32

# Semantic boundary configuration.
SEMANTIC_PERCENTILE = 20

MIN_SEMANTIC_THRESHOLD = 0.45
MAX_SEMANTIC_THRESHOLD = 0.80


# ============================================================
# EMBEDDINGS
# ============================================================

def embed_batch(
    texts,
    batch_size=32,
    max_retries=3
):
    """
    Generate Mistral embeddings in batches.
    """

    if not texts:
        return []

    all_embeddings = []

    for batch_start in range(
        0,
        len(texts),
        batch_size
    ):

        batch = texts[
            batch_start:
            batch_start + batch_size
        ]

        batch_embeddings = None

        for attempt in range(
            max_retries
        ):

            try:

                response = client.embeddings.create(
                    model="mistral-embed",
                    inputs=batch
                )

                batch_embeddings = [
                    item.embedding
                    for item in response.data
                ]

                break

            except SDKError as e:

                error_message = str(e)

                if (
                    "429" in error_message
                    or
                    "rate_limited"
                    in error_message.lower()
                ):

                    if attempt < max_retries - 1:

                        wait_time = 2 ** attempt

                        print(
                            "Rate limit hit. "
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(
                            wait_time
                        )

                    else:

                        raise Exception(
                            "Rate limit exceeded after "
                            f"{max_retries} attempts."
                        )

                else:

                    raise

        if batch_embeddings is None:

            raise Exception(
                "Failed to generate embeddings."
            )

        all_embeddings.extend(
            batch_embeddings
        )

    return all_embeddings


# ============================================================
# FILE UTILITIES
# ============================================================

def get_extension(filename):
    """
    Return lowercase file extension.
    """

    return os.path.splitext(
        filename.lower()
    )[1]


def clean_text(text):
    """
    Normalize extracted text while preserving paragraph
    boundaries.
    """

    lines = []

    previous_blank = False

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:

            if not previous_blank:

                lines.append("")

            previous_blank = True

            continue

        lines.append(line)

        previous_blank = False

    return "\n".join(
        lines
    ).strip()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(content):
    """
    Extract text from a text-based PDF.
    """

    try:

        pdf_file = io.BytesIO(
            content
        )

        reader = PdfReader(
            pdf_file
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = (
                page.extract_text()
                or ""
            )

            page_text = clean_text(
                page_text
            )

            if page_text:

                pages.append(
                    f"[Page {page_number}]\n"
                    f"{page_text}"
                )

        text = "\n\n".join(
            pages
        )

        if not text:

            raise ValueError(
                "No extractable text was found "
                "in this PDF. This may be a "
                "scanned/image-only PDF."
            )

        return text

    except ValueError:

        raise

    except Exception as e:

        raise ValueError(
            f"Failed to extract text from PDF: {str(e)}"
        )


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_docx_text(content):
    """
    Extract paragraphs and tables from DOCX.
    """

    try:

        document = Document(
            io.BytesIO(content)
        )

        parts = []

        for element in (
            document.element.body.iterchildren()
        ):

            # ------------------------------------------------
            # Paragraph
            # ------------------------------------------------

            if element.tag.endswith(
                "}p"
            ):

                paragraph_text = "".join(
                    node.text or ""
                    for node in element.iter()
                    if node.tag.endswith(
                        "}t"
                    )
                ).strip()

                if paragraph_text:

                    parts.append(
                        paragraph_text
                    )

            # ------------------------------------------------
            # Table
            # ------------------------------------------------

            elif element.tag.endswith(
                "}tbl"
            ):

                table_rows = []

                for row in (
                    element.iterchildren()
                ):

                    if not row.tag.endswith(
                        "}tr"
                    ):

                        continue

                    cells = []

                    for cell in (
                        row.iterchildren()
                    ):

                        if not cell.tag.endswith(
                            "}tc"
                        ):

                            continue

                        cell_text = " ".join(
                            (
                                node.text
                                or ""
                            ).strip()
                            for node in cell.iter()
                            if (
                                node.tag.endswith(
                                    "}t"
                                )
                                and (
                                    node.text
                                    or ""
                                ).strip()
                            )
                        )

                        cells.append(
                            cell_text
                        )

                    if cells:

                        table_rows.append(
                            " | ".join(
                                cells
                            )
                        )

                if table_rows:

                    parts.append(
                        "[Table]\n"
                        + "\n".join(
                            table_rows
                        )
                    )

        text = clean_text(
            "\n\n".join(parts)
        )

        if not text:

            raise ValueError(
                "The DOCX file contains no "
                "extractable text."
            )

        return text

    except ValueError:

        raise

    except Exception as e:

        raise ValueError(
            f"Failed to extract text from DOCX: {str(e)}"
        )


# ============================================================
# IMAGE OCR
# ============================================================

def extract_image_text(
    filename,
    content
):
    """
    Extract text from PNG/JPG/JPEG using Mistral OCR.
    """

    extension = get_extension(
        filename
    )

    mime_type = IMAGE_MIME_TYPES.get(
        extension
    )

    if not mime_type:

        raise ValueError(
            "Unsupported image format."
        )

    try:

        encoded_image = base64.b64encode(
            content
        ).decode(
            "utf-8"
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{encoded_image}"
        )

        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": image_data_url,
            },
        )

        pages = getattr(
            response,
            "pages",
            []
        )

        extracted_pages = []

        for page in pages:

            page_text = getattr(
                page,
                "markdown",
                ""
            ) or ""

            page_text = clean_text(
                page_text
            )

            if page_text:

                extracted_pages.append(
                    page_text
                )

        text = "\n\n".join(
            extracted_pages
        ).strip()

        if not text:

            raise ValueError(
                "No readable text was found "
                "in the uploaded image."
            )

        return text

    except Exception as e:

        raise ValueError(
            f"Failed to OCR image: {str(e)}"
        )


# ============================================================
# UNIFIED EXTRACTION
# ============================================================

def extract_text_from_file(
    filename,
    content
):
    """
    Convert supported files into text.
    """

    extension = get_extension(
        filename
    )

    if extension not in SUPPORTED_EXTENSIONS:

        supported = ", ".join(
            sorted(
                SUPPORTED_EXTENSIONS
            )
        )

        raise ValueError(
            f"Unsupported file format "
            f"'{extension or 'unknown'}'. "
            f"Supported formats: {supported}"
        )

    if not content:

        raise ValueError(
            "The uploaded file is empty."
        )

    if extension == ".pdf":

        return extract_pdf_text(
            content
        )

    if extension == ".docx":

        return extract_docx_text(
            content
        )

    if extension in IMAGE_MIME_TYPES:

        return extract_image_text(
            filename,
            content
        )

    # TXT

    text = content.decode(
        "utf-8",
        errors="ignore"
    )

    text = clean_text(
        text
    )

    if not text:

        raise ValueError(
            "The uploaded text file is empty."
        )

    return text


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_into_sentences(text):
    """
    Split text into sentence-like units.

    Supports common English and multilingual sentence
    terminators.
    """

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    sentences = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:

            continue

        parts = re.split(
            r"(?<=[.!?。！？])\s+",
            paragraph
        )

        for part in parts:

            sentence = part.strip()

            if sentence:

                sentences.append(
                    sentence
                )

    return sentences


# ============================================================
# MISTRAL TOKEN COUNTING
# ============================================================

def count_tokens(text):
    """
    Count tokens using the actual underlying Mistral
    tokenizer.

    IMPORTANT:

    MistralTokenizer is a wrapper around the instruct
    tokenizer, which itself contains the underlying
    tokenizer.

    The underlying tokenizer exposes:

        encode(text, bos=False, eos=False)

    We intentionally use that API instead of
    encode_chat_completion() because we only need the
    token count of raw text.
    """

    if not text:

        return 0

    try:

        token_ids = (
            tokenizer
            .instruct_tokenizer
            .tokenizer
            .encode(
                text,
                bos=False,
                eos=False
            )
        )

        return len(
            token_ids
        )

    except Exception as e:

        print(
            "Tokenizer error: "
            f"{e}"
        )

        # Conservative emergency fallback.
        #
        # This should NOT normally execute.
        return max(
            1,
            len(text) // 4
        )


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    vector_a,
    vector_b
):
    """
    Calculate cosine similarity.
    """

    a = np.asarray(
        vector_a,
        dtype="float32"
    )

    b = np.asarray(
        vector_b,
        dtype="float32"
    )

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:

        return 0.0

    return float(
        np.dot(a, b)
        / denominator
    )


# ============================================================
# ADAPTIVE SEMANTIC THRESHOLD
# ============================================================

def calculate_semantic_threshold(
    similarities
):
    """
    Calculate an adaptive semantic boundary threshold.

    Very small documents use a conservative fallback because
    a percentile calculated from only a few observations is
    unstable.
    """

    if not similarities:

        return MIN_SEMANTIC_THRESHOLD

    if len(similarities) < 5:

        return 0.65

    values = np.asarray(
        similarities,
        dtype="float32"
    )

    threshold = float(
        np.percentile(
            values,
            SEMANTIC_PERCENTILE
        )
    )

    threshold = max(
        MIN_SEMANTIC_THRESHOLD,
        threshold
    )

    threshold = min(
        MAX_SEMANTIC_THRESHOLD,
        threshold
    )

    return threshold


# ============================================================
# CREATE OVERLAP
# ============================================================

def create_overlap(
    sentences
):
    """
    Create sentence-level overlap up to OVERLAP_TOKENS.
    """

    overlap = []

    total_tokens = 0

    for sentence in reversed(
        sentences
    ):

        sentence_tokens = count_tokens(
            sentence
        )

        if (
            overlap
            and
            total_tokens
            + sentence_tokens
            > OVERLAP_TOKENS
        ):

            break

        overlap.insert(
            0,
            sentence
        )

        total_tokens += (
            sentence_tokens
        )

        if total_tokens >= OVERLAP_TOKENS:

            break

    return overlap


# ============================================================
# LARGE SENTENCE SPLITTING
# ============================================================

def split_large_sentence(
    sentence
):
    """
    Split an unusually large sentence by words while
    respecting MAX_CHUNK_TOKENS.
    """

    words = sentence.split()

    chunks = []

    current_words = []

    current_tokens = 0

    for word in words:

        word_tokens = count_tokens(
            word
        )

        # ----------------------------------------------------
        # Extremely large single word.
        # ----------------------------------------------------

        if word_tokens > MAX_CHUNK_TOKENS:

            if current_words:

                chunks.append(
                    " ".join(
                        current_words
                    )
                )

                current_words = []

                current_tokens = 0

            chunks.append(
                word
            )

            continue

        # ----------------------------------------------------
        # Would exceed maximum?
        # ----------------------------------------------------

        if (
            current_words
            and
            current_tokens
            + word_tokens
            > MAX_CHUNK_TOKENS
        ):

            chunks.append(
                " ".join(
                    current_words
                )
            )

            # ----------------------------------------------
            # Build word overlap.
            # ----------------------------------------------

            overlap_words = []

            overlap_tokens = 0

            for previous_word in reversed(
                current_words
            ):

                previous_tokens = count_tokens(
                    previous_word
                )

                if (
                    overlap_words
                    and
                    overlap_tokens
                    + previous_tokens
                    > OVERLAP_TOKENS
                ):

                    break

                overlap_words.insert(
                    0,
                    previous_word
                )

                overlap_tokens += (
                    previous_tokens
                )

            # ----------------------------------------------
            # Ensure overlap + new word fits.
            # ----------------------------------------------

            while (
                overlap_words
                and
                overlap_tokens
                + word_tokens
                > MAX_CHUNK_TOKENS
            ):

                removed = (
                    overlap_words.pop(0)
                )

                overlap_tokens -= (
                    count_tokens(
                        removed
                    )
                )

            current_words = (
                overlap_words
                + [word]
            )

            current_tokens = (
                overlap_tokens
                + word_tokens
            )

        else:

            current_words.append(
                word
            )

            current_tokens += (
                word_tokens
            )

    if current_words:

        chunks.append(
            " ".join(
                current_words
            )
        )

    return chunks


# ============================================================
# ADAPTIVE SEMANTIC + TOKEN-AWARE CHUNKING
# ============================================================

def adaptive_chunk_text(
    text
):
    """
    Adaptive chunking pipeline:

        1. Sentence segmentation
        2. Sentence embeddings
        3. Adjacent cosine similarity
        4. Adaptive semantic threshold
        5. Token-aware chunk construction
        6. Sentence overlap
        7. Final hard token validation
    """

    sentences = split_into_sentences(
        text
    )

    if not sentences:

        return [text]

    # --------------------------------------------------------
    # Single sentence
    # --------------------------------------------------------

    if len(sentences) == 1:

        token_count = count_tokens(
            sentences[0]
        )

        if token_count <= MAX_CHUNK_TOKENS:

            return sentences

        return split_large_sentence(
            sentences[0]
        )

    # --------------------------------------------------------
    # Sentence embeddings
    # --------------------------------------------------------

    sentence_embeddings = embed_batch(
        sentences,
        batch_size=SENTENCE_EMBED_BATCH_SIZE
    )

    # --------------------------------------------------------
    # Adjacent sentence similarity
    # --------------------------------------------------------

    similarities = []

    for i in range(
        len(sentence_embeddings) - 1
    ):

        similarities.append(
            cosine_similarity(
                sentence_embeddings[i],
                sentence_embeddings[i + 1]
            )
        )

    # --------------------------------------------------------
    # Adaptive threshold
    # --------------------------------------------------------

    semantic_threshold = (
        calculate_semantic_threshold(
            similarities
        )
    )

    print(
        "Semantic chunking threshold: "
        f"{semantic_threshold:.4f}"
    )

    # --------------------------------------------------------
    # Build sentence groups
    # --------------------------------------------------------

    raw_chunks = []

    current_sentences = []

    current_tokens = 0

    for i, sentence in enumerate(
        sentences
    ):

        sentence_tokens = count_tokens(
            sentence
        )

        # ----------------------------------------------------
        # Extremely large sentence
        # ----------------------------------------------------

        if sentence_tokens > MAX_CHUNK_TOKENS:

            if current_sentences:

                raw_chunks.append(
                    current_sentences
                )

                current_sentences = []

                current_tokens = 0

            large_chunks = (
                split_large_sentence(
                    sentence
                )
            )

            for large_chunk in large_chunks:

                raw_chunks.append(
                    [large_chunk]
                )

            continue

        # ----------------------------------------------------
        # Hard maximum check
        # ----------------------------------------------------

        if (
            current_sentences
            and
            current_tokens
            + sentence_tokens
            > MAX_CHUNK_TOKENS
        ):

            # Finalize current chunk.
            raw_chunks.append(
                current_sentences
            )

            # Create overlap.
            overlap = create_overlap(
                current_sentences
            )

            current_sentences = []

            current_tokens = 0

            # ------------------------------------------------
            # Add only overlap that still leaves room for
            # the new sentence.
            # ------------------------------------------------

            for overlap_sentence in reversed(
                overlap
            ):

                overlap_tokens = count_tokens(
                    overlap_sentence
                )

                if (
                    current_tokens
                    + overlap_tokens
                    + sentence_tokens
                    <= MAX_CHUNK_TOKENS
                ):

                    current_sentences.insert(
                        0,
                        overlap_sentence
                    )

                    current_tokens += (
                        overlap_tokens
                    )

            # Add current sentence.

            if (
                current_tokens
                + sentence_tokens
                <= MAX_CHUNK_TOKENS
            ):

                current_sentences.append(
                    sentence
                )

                current_tokens += (
                    sentence_tokens
                )

            else:

                # Safety fallback.
                raw_chunks.append(
                    [sentence]
                )

                current_sentences = []

                current_tokens = 0

            continue

        # ----------------------------------------------------
        # Semantic boundary
        # ----------------------------------------------------

        semantic_boundary = False

        if i > 0:

            previous_similarity = (
                similarities[i - 1]
            )

            semantic_boundary = (
                previous_similarity
                < semantic_threshold
            )

        # ----------------------------------------------------
        # Split only if the existing chunk is large enough.
        # ----------------------------------------------------

        if (
            semantic_boundary
            and
            current_sentences
            and
            current_tokens
            >= MIN_CHUNK_TOKENS
        ):

            raw_chunks.append(
                current_sentences
            )

            overlap = create_overlap(
                current_sentences
            )

            current_sentences = []

            current_tokens = 0

            # Add overlap only when it fits.

            for overlap_sentence in reversed(
                overlap
            ):

                overlap_tokens = count_tokens(
                    overlap_sentence
                )

                if (
                    current_tokens
                    + overlap_tokens
                    + sentence_tokens
                    <= MAX_CHUNK_TOKENS
                ):

                    current_sentences.insert(
                        0,
                        overlap_sentence
                    )

                    current_tokens += (
                        overlap_tokens
                    )

            # Add new sentence.

            if (
                current_tokens
                + sentence_tokens
                <= MAX_CHUNK_TOKENS
            ):

                current_sentences.append(
                    sentence
                )

                current_tokens += (
                    sentence_tokens
                )

            continue

        # ----------------------------------------------------
        # Normal addition
        # ----------------------------------------------------

        current_sentences.append(
            sentence
        )

        current_tokens += (
            sentence_tokens
        )

        # ----------------------------------------------------
        # End of document
        # ----------------------------------------------------

        if i == len(sentences) - 1:

            raw_chunks.append(
                current_sentences
            )

            current_sentences = []

            current_tokens = 0

    # --------------------------------------------------------
    # Convert groups to text
    # --------------------------------------------------------

    chunks = []

    for sentence_group in raw_chunks:

        chunk = " ".join(
            sentence_group
        ).strip()

        if chunk:

            chunks.append(
                chunk
            )

    # --------------------------------------------------------
    # FINAL HARD TOKEN VALIDATION
    # --------------------------------------------------------

    final_chunks = []

    for chunk in chunks:

        token_count = count_tokens(
            chunk
        )

        if token_count <= MAX_CHUNK_TOKENS:

            final_chunks.append(
                chunk
            )

        else:

            print(
                "Hard token limit exceeded: "
                f"{token_count}. "
                "Splitting chunk..."
            )

            split_chunks = (
                split_large_sentence(
                    chunk
                )
            )

            final_chunks.extend(
                split_chunks
            )

    # --------------------------------------------------------
    # Remove duplicates / empty chunks
    # --------------------------------------------------------

    cleaned_chunks = []

    for chunk in final_chunks:

        chunk = chunk.strip()

        if not chunk:

            continue

        if (
            cleaned_chunks
            and
            chunk
            == cleaned_chunks[-1]
        ):

            continue

        cleaned_chunks.append(
            chunk
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print(
        "Adaptive chunking complete:"
    )

    print(
        f"  Sentences: {len(sentences)}"
    )

    print(
        f"  Chunks: {len(cleaned_chunks)}"
    )

    if cleaned_chunks:

        token_sizes = [
            count_tokens(chunk)
            for chunk in cleaned_chunks
        ]

        print(
            f"  Min tokens: "
            f"{min(token_sizes)}"
        )

        print(
            f"  Max tokens: "
            f"{max(token_sizes)}"
        )

        print(
            f"  Avg tokens: "
            f"{sum(token_sizes) / len(token_sizes):.1f}"
        )

        # ----------------------------------------------------
        # HARD INVARIANT
        # ----------------------------------------------------

        if any(
            size > MAX_CHUNK_TOKENS
            for size in token_sizes
        ):

            raise RuntimeError(
                "Chunking invariant violated: "
                "a final chunk exceeds "
                f"{MAX_CHUNK_TOKENS} tokens."
            )

    return cleaned_chunks


# ============================================================
# FAISS INDEX
# ============================================================

def create_faiss_index(
    chunks
):
    """
    Generate embeddings for final chunks and create
    a FAISS IndexFlatL2 index.
    """

    if not chunks:

        raise ValueError(
            "No chunks were created."
        )

    vectors = embed_batch(
        chunks,
        batch_size=CHUNK_EMBED_BATCH_SIZE
    )

    if not vectors:

        raise ValueError(
            "Failed to generate embeddings."
        )

    dimension = len(
        vectors[0]
    )

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(
        np.array(
            vectors
        ).astype(
            "float32"
        )
    )

    return index


# ============================================================
# MAIN INGESTION
# ============================================================

def ingest_file(
    filename,
    content
):
    """
    Complete ingestion pipeline:

        File
          ↓
        Text extraction
          ↓
        Sentence segmentation
          ↓
        Sentence embeddings
          ↓
        Semantic boundary detection
          ↓
        Token-aware adaptive chunking
          ↓
        Chunk embeddings
          ↓
        FAISS
    """

    print(
        f"\nStarting ingestion: {filename}"
    )

    # --------------------------------------------------------
    # 1. Extract text
    # --------------------------------------------------------

    text = extract_text_from_file(
        filename,
        content
    )

    print(
        f"Extracted text length: "
        f"{len(text)} characters"
    )

    # --------------------------------------------------------
    # 2. Adaptive chunking
    # --------------------------------------------------------

    chunks = adaptive_chunk_text(
        text
    )

    if not chunks:

        raise ValueError(
            "No chunks were created "
            "from the document."
        )

    # --------------------------------------------------------
    # 3. Create FAISS index
    # --------------------------------------------------------

    index = create_faiss_index(
        chunks
    )

    # --------------------------------------------------------
    # 4. Save FAISS
    # --------------------------------------------------------

    faiss.write_index(
        index,
        INDEX_FILE
    )

    # --------------------------------------------------------
    # 5. Save chunks
    # --------------------------------------------------------

    with open(
        DOCS_FILE,
        "wb"
    ) as f:

        pickle.dump(
            chunks,
            f
        )

    print(
        f"Successfully indexed "
        f"{len(chunks)} adaptive chunks "
        f"from {filename}"
    )

    print(
        "FAISS index updated successfully.\n"
    )