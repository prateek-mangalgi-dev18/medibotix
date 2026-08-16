import base64
import io
import os
import pickle
import time

import faiss
import numpy as np
from docx import Document
from mistralai import Mistral
from mistralai.models.sdkerror import SDKError
from pypdf import PdfReader

from config import MISTRAL_API_KEY


client = Mistral(api_key=MISTRAL_API_KEY)

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
# EMBEDDINGS
# ============================================================

def embed_batch(texts, max_retries=3):
    """
    Generate embeddings for multiple text chunks.

    Uses Mistral's embedding model with retry logic
    for rate-limit errors.
    """

    for attempt in range(max_retries):

        try:

            response = client.embeddings.create(
                model="mistral-embed",
                inputs=texts
            )

            return [
                item.embedding
                for item in response.data
            ]

        except SDKError as e:

            error_message = str(e)

            if (
                "429" in error_message
                or "rate_limited" in error_message.lower()
            ):

                if attempt < max_retries - 1:

                    wait_time = 2 ** attempt

                    print(
                        f"Rate limit hit. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                else:

                    raise Exception(
                        "Rate limit exceeded after "
                        f"{max_retries} attempts. "
                        "Please try again later."
                    )

            else:

                raise


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_extension(filename):
    """
    Return the lowercase file extension.
    """

    return os.path.splitext(
        filename.lower()
    )[1]


def clean_text(text):
    """
    Normalize extracted text.

    Removes empty lines and unnecessary whitespace
    without changing the actual content.
    """

    lines = []

    for line in text.splitlines():

        cleaned = line.strip()

        if cleaned:

            lines.append(cleaned)

    return "\n".join(lines).strip()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(content):
    """
    Extract text from a normal text-based PDF.

    Scanned/image-only PDFs will be handled by the
    OCR pipeline in the next development step.
    """

    try:

        pdf_file = io.BytesIO(content)

        reader = PdfReader(pdf_file)

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = page.extract_text() or ""

            page_text = clean_text(page_text)

            if page_text:

                pages.append(
                    f"[Page {page_number}]\n"
                    f"{page_text}"
                )

        text = "\n\n".join(pages)

        if not text:

            raise ValueError(
                "No extractable text was found in this PDF. "
                "This may be a scanned/image-only PDF."
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
    Extract paragraphs and tables from a DOCX file.

    Paragraphs and tables are processed in their original
    document order.
    """

    try:

        document = Document(
            io.BytesIO(content)
        )

        parts = []

        # ----------------------------------------------------
        # Walk through the DOCX body directly so that
        # paragraphs and tables remain in their original order.
        # ----------------------------------------------------

        for element in document.element.body.iterchildren():

            # ----------------------------------------------
            # Paragraph
            # ----------------------------------------------

            if element.tag.endswith("}p"):

                paragraph_text = "".join(
                    node.text or ""
                    for node in element.iter()
                    if node.tag.endswith("}t")
                ).strip()

                if paragraph_text:

                    parts.append(
                        paragraph_text
                    )

            # ----------------------------------------------
            # Table
            # ----------------------------------------------

            elif element.tag.endswith("}tbl"):

                table_rows = []

                for row in element.iterchildren():

                    if not row.tag.endswith("}tr"):

                        continue

                    cells = []

                    for cell in row.iterchildren():

                        if not cell.tag.endswith("}tc"):

                            continue

                        cell_text = " ".join(
                            (
                                node.text or ""
                            ).strip()
                            for node in cell.iter()
                            if (
                                node.tag.endswith("}t")
                                and (node.text or "").strip()
                            )
                        )

                        cells.append(
                            cell_text
                        )

                    if cells:

                        table_rows.append(
                            " | ".join(cells)
                        )

                if table_rows:

                    parts.append(
                        "[Table]\n"
                        + "\n".join(table_rows)
                    )

        text = clean_text(
            "\n".join(parts)
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

def extract_image_text(filename, content):
    """
    Extract text from PNG/JPG/JPEG using
    Mistral OCR.
    """

    extension = get_extension(filename)

    mime_type = IMAGE_MIME_TYPES.get(
        extension
    )

    if not mime_type:

        raise ValueError(
            "Unsupported image format."
        )

    try:

        # Convert image bytes to Base64
        encoded_image = base64.b64encode(
            content
        ).decode("utf-8")

        # Create a data URL accepted by Mistral OCR
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
# UNIFIED TEXT EXTRACTION
# ============================================================

def extract_text_from_file(filename, content):
    """
    Unified document ingestion layer.

    Every supported file type is converted into
    a common text representation.

    Supported:

        PDF
        DOCX
        PNG
        JPG
        JPEG
        TXT
    """

    extension = get_extension(
        filename
    )

    if extension not in SUPPORTED_EXTENSIONS:

        supported = ", ".join(
            sorted(SUPPORTED_EXTENSIONS)
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

    # ========================================================
    # PDF
    # ========================================================

    if extension == ".pdf":

        return extract_pdf_text(
            content
        )

    # ========================================================
    # DOCX
    # ========================================================

    if extension == ".docx":

        return extract_docx_text(
            content
        )

    # ========================================================
    # IMAGE
    # ========================================================

    if extension in IMAGE_MIME_TYPES:

        return extract_image_text(
            filename,
            content
        )

    # ========================================================
    # TXT
    # ========================================================

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
# INGESTION PIPELINE
# ============================================================

def ingest_file(filename, content):
    """
    Complete ingestion pipeline.

    Current pipeline:

        File
          ↓
        Extraction
          ↓
        Current fixed-size chunking
          ↓
        Mistral embeddings
          ↓
        FAISS

    The chunking algorithm will be upgraded in the
    next development step.
    """

    # --------------------------------------------------------
    # 1. Extract text
    # --------------------------------------------------------

    text = extract_text_from_file(
        filename,
        content
    )

    # --------------------------------------------------------
    # 2. CURRENT CHUNKING
    #
    # IMPORTANT:
    # We intentionally keep your existing chunking here.
    #
    # This will be replaced with adaptive semantic
    # token-aware chunking in the next step.
    # --------------------------------------------------------

    chunks = [
        text[i:i + 500]
        for i in range(
            0,
            len(text),
            450
        )
    ]

    if not chunks:

        chunks = [
            text
        ]

    # --------------------------------------------------------
    # 3. Generate embeddings
    # --------------------------------------------------------

    vectors = embed_batch(
        chunks
    )

    if not vectors:

        raise ValueError(
            "Failed to generate embeddings "
            "for the document."
        )

    # --------------------------------------------------------
    # 4. Create FAISS index
    # --------------------------------------------------------

    dimension = len(
        vectors[0]
    )

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(
        np.array(
            vectors
        ).astype("float32")
    )

    # --------------------------------------------------------
    # 5. Save FAISS index
    # --------------------------------------------------------

    faiss.write_index(
        index,
        INDEX_FILE
    )

    # --------------------------------------------------------
    # 6. Save chunks
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
        f"{len(chunks)} chunks from {filename}"
    )