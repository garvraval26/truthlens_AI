"""
utils.py
==============================================================
Shared utility functions for the Fake News Detection and Media
Bias Analysis System.

Responsibilities:
    - Parse uploaded files (txt, pdf, docx) into plain text
    - Fetch and parse news articles from a URL
    - Input validation (URLs, empty text, file size/type)
    - Text cleaning helpers
    - Formatting helpers used across pages (dates, percentages)
==============================================================
"""

import io
import re
import logging
import validators
import requests
from datetime import datetime

from config import (
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_SIZE_MB,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==============================================================
# CUSTOM EXCEPTIONS
# ==============================================================
class InvalidInputError(Exception):
    """Raised for user-facing input validation failures."""
    pass


class FileParsingError(Exception):
    """Raised when an uploaded file cannot be parsed."""
    pass


class URLFetchError(Exception):
    """Raised when a news URL cannot be fetched/parsed."""
    pass


# ==============================================================
# TEXT VALIDATION
# ==============================================================
def validate_text_input(text: str, min_length: int = 20) -> None:
    """
    Validates that pasted/extracted text is usable for analysis.
    Raises InvalidInputError with a user-friendly message if not.
    """
    if text is None or not text.strip():
        raise InvalidInputError(
            "The article text is empty. Please paste some content or upload a valid file."
        )
    if len(text.strip()) < min_length:
        raise InvalidInputError(
            f"The article text is too short (minimum {min_length} characters) "
            f"for a reliable analysis."
        )


def clean_text(text: str) -> str:
    """
    Normalizes whitespace and strips control characters from
    extracted/pasted text before feeding it to the model.
    """
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text.strip()


# ==============================================================
# FILE PARSING (txt / pdf / docx)
# ==============================================================
def validate_uploaded_file(uploaded_file) -> None:
    """
    Validates file extension and size before parsing.
    Raises FileParsingError on failure.
    """
    if uploaded_file is None:
        raise FileParsingError("No file was uploaded.")

    extension = uploaded_file.name.split(".")[-1].lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise FileParsingError(
            f"Unsupported file type '.{extension}'. "
            f"Allowed types: {', '.join(ALLOWED_UPLOAD_EXTENSIONS)}."
        )

    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise FileParsingError(
            f"File is too large ({size_mb:.2f} MB). "
            f"Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB."
        )


def parse_txt_file(uploaded_file) -> str:
    """Extracts text content from a plain .txt upload."""
    try:
        raw_bytes = uploaded_file.read()
        text = raw_bytes.decode("utf-8", errors="ignore")
        return clean_text(text)
    except Exception as e:
        raise FileParsingError(f"Could not read the .txt file: {e}")


def parse_pdf_file(uploaded_file) -> str:
    """Extracts text content from a .pdf upload using PyPDF2."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        if len(reader.pages) == 0:
            raise FileParsingError("The PDF file appears to be empty.")

        text_chunks = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

        full_text = "\n".join(text_chunks)
        if not full_text.strip():
            raise FileParsingError(
                "No extractable text found in the PDF. "
                "It may be a scanned/image-based document."
            )
        return clean_text(full_text)
    except FileParsingError:
        raise
    except Exception as e:
        raise FileParsingError(f"The PDF file appears to be corrupted or unreadable: {e}")


def parse_docx_file(uploaded_file) -> str:
    """Extracts text content from a .docx upload using python-docx."""
    try:
        from docx import Document

        doc = Document(io.BytesIO(uploaded_file.read()))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)

        if not full_text.strip():
            raise FileParsingError("No extractable text found in the Word document.")
        return clean_text(full_text)
    except FileParsingError:
        raise
    except Exception as e:
        raise FileParsingError(f"The DOCX file appears to be corrupted or unreadable: {e}")


def extract_text_from_upload(uploaded_file) -> str:
    """
    Master dispatcher: validates and extracts text from an uploaded
    file regardless of type (txt/pdf/docx).
    """
    validate_uploaded_file(uploaded_file)
    extension = uploaded_file.name.split(".")[-1].lower()

    if extension == "txt":
        return parse_txt_file(uploaded_file)
    elif extension == "pdf":
        return parse_pdf_file(uploaded_file)
    elif extension == "docx":
        return parse_docx_file(uploaded_file)
    else:
        # Should never reach here due to validate_uploaded_file, but
        # kept as a defensive fallback.
        raise FileParsingError(f"Unsupported file type: .{extension}")


# ==============================================================
# URL VALIDATION & ARTICLE EXTRACTION
# ==============================================================
def validate_url(url: str) -> None:
    """Validates that a string is a well-formed, reachable-looking URL."""
    if not url or not url.strip():
        raise InvalidInputError("Please enter a news article URL.")

    if not validators.url(url):
        raise InvalidInputError(
            "The URL entered is not valid. Please check the format "
            "(e.g. https://example.com/article)."
        )


def check_internet_connection() -> bool:
    """Quick connectivity check used before attempting URL fetches."""
    try:
        requests.get("https://www.google.com", timeout=4)
        return True
    except requests.RequestException:
        return False


def fetch_article_from_url(url: str) -> dict:
    """
    Fetches and parses a news article from a URL using newspaper3k.

    Returns:
        {
            "title": str,
            "text": str,
            "authors": list,
            "publish_date": str or None,
            "top_image": str or None,
            "source_domain": str,
        }
    """
    validate_url(url)

    if not check_internet_connection():
        raise URLFetchError(
            "No internet connection detected. Please check your network "
            "and try again."
        )

    try:
        from newspaper import Article

        article = Article(url, browser_user_agent=USER_AGENT, request_timeout=REQUEST_TIMEOUT_SECONDS)
        article.download()

        # newspaper3k does NOT raise on 403/404: it silently leaves article.html empty
        # and only fails later in parse(). So check for that and use a fallback fetch.
        if not article.html:
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Referer": "https://www.google.com/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
            }
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
            if resp.status_code in (401, 402, 403, 429):
                raise URLFetchError(
                    "This website blocks automated access or requires a subscription "
                    f"(HTTP {resp.status_code}). Try a different news source, or copy the "
                    "article text and paste it into the News Detector page."
                )
            resp.raise_for_status()
            article = Article(url)
            article.set_html(resp.text)

        article.parse()

        if not article.text or not article.text.strip():
            raise URLFetchError(
                "Could not extract readable article content from this URL. "
                "The page may not be a standard news article."
            )

        domain_match = re.search(r"https?://(www\.)?([^/]+)", url)
        source_domain = domain_match.group(2) if domain_match else url

        return {
            "title": article.title or "Untitled Article",
            "text": clean_text(article.text),
            "authors": article.authors or [],
            "publish_date": (
                article.publish_date.strftime("%Y-%m-%d")
                if article.publish_date
                else None
            ),
            "top_image": article.top_image or None,
            "source_domain": source_domain,
        }

    except URLFetchError:
        raise
    except Exception as e:
        logger.error(f"Article extraction failed for {url}: {e}")
        raise URLFetchError(
            f"Failed to fetch or parse the article from this URL. "
            f"It may be blocked, paywalled, or not a valid news page. "
            f"Details: {e}"
        )


# ==============================================================
# FORMATTING HELPERS
# ==============================================================
def format_percentage(value: float) -> str:
    """Converts a 0-1 float into a display percentage string."""
    try:
        return f"{value * 100:.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_datetime(dt_string: str, fmt_out: str = "%b %d, %Y • %I:%M %p") -> str:
    """Reformats a stored timestamp string into a friendly display format."""
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        return dt.strftime(fmt_out)
    except (ValueError, TypeError):
        return dt_string or "Unknown"


def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncates text to a max length, adding an ellipsis if cut."""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def get_confidence_label(confidence: float) -> str:
    """Maps a numeric confidence score to a human-readable label."""
    if confidence >= 0.80:
        return "High Confidence"
    elif confidence >= 0.55:
        return "Moderate Confidence"
    else:
        return "Low Confidence"


def get_bias_emoji(bias_label: str) -> str:
    """Returns an emoji indicator for a given bias classification."""
    mapping = {
        "left-leaning": "⬅️",
        "center / neutral": "⚖️",
        "right-leaning": "➡️",
    }
    return mapping.get(bias_label, "❓")