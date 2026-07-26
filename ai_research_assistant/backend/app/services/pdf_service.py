import os
import re
from typing import List, Dict, Any
from pypdf import PdfReader

class PDFExtractionError(Exception):
    pass

class PDFService:
    @staticmethod
    def extract_text_by_page(file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from each page of a PDF document.
        Returns a list of dicts: [{'page_number': int, 'text': str}]
        """
        if not os.path.exists(file_path):
            raise PDFExtractionError(f"File not found at path: {file_path}")

        extracted_pages = []
        try:
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                raw_text = page.extract_text() or ""
                cleaned_text = PDFService.clean_text(raw_text)
                extracted_pages.append({
                    "page_number": idx + 1,
                    "text": cleaned_text
                })
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract PDF text: {str(e)}")

        return extracted_pages

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and normalizes extracted text.
        Removes excessive whitespace, null characters, and common PDF artifacts.
        """
        if not text:
            return ""
        # Remove null characters
        text = text.replace('\x00', '')
        # Standardize newlines
        text = re.sub(r'\r\n|\r', '\n', text)
        # Collapse multiple spaces (excluding newlines)
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove excessive empty lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
