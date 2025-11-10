"""
Text extraction utilities for various file formats.
"""

import json
import logging
from typing import Optional
import io

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from various file formats."""

    def extract_from_bytes(self, content: bytes, file_type: str) -> str:
        """
        Extract text from file bytes.

        Args:
            content: File content as bytes
            file_type: File extension (txt, json, pdf, docx)

        Returns:
            Extracted text
        """
        try:
            if file_type == 'txt':
                return content.decode('utf-8')

            elif file_type == 'json':
                data = json.loads(content.decode('utf-8'))
                return self._extract_text_from_json(data)

            elif file_type == 'pdf':
                return self._extract_from_pdf(content)

            elif file_type == 'docx':
                return self._extract_from_docx(content)

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}", exc_info=True)
            raise

    def _extract_text_from_json(self, data) -> str:
        """Recursively extract text from JSON data."""
        if isinstance(data, dict):
            return '\n'.join([
                f"{k}: {self._extract_text_from_json(v)}"
                for k, v in data.items()
            ])
        elif isinstance(data, list):
            return '\n'.join([self._extract_text_from_json(item) for item in data])
        else:
            return str(data)

    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=content, filetype="pdf")
            text = ""

            for page in doc:
                text += page.get_text()

            return text

        except ImportError:
            logger.error("PyMuPDF not installed. Install with: pip install pymupdf")
            raise
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}", exc_info=True)
            raise

    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document

            doc = Document(io.BytesIO(content))
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

            return text

        except ImportError:
            logger.error("python-docx not installed. Install with: pip install python-docx")
            raise
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}", exc_info=True)
            raise
