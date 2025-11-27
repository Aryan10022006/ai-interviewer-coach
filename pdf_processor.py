"""
PDF Resume Processor
Extracts text from PDF resumes using multiple methods for robustness.
"""

import io
from typing import Optional

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("⚠️ PyPDF2 not installed. Run: pip install PyPDF2")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("⚠️ pdfplumber not installed. Run: pip install pdfplumber")


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF file using multiple methods.
    Falls back to alternative methods if primary fails.
    
    Args:
        pdf_file: File-like object (from Streamlit file_uploader)
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If no PDF library is available or extraction fails
    """
    
    if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
        raise ValueError("No PDF processing library available. Install PyPDF2 or pdfplumber.")
    
    # Read file bytes
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)  # Reset file pointer for potential re-reads
    
    text = ""
    
    # Method 1: Try pdfplumber (better for complex layouts)
    if PDFPLUMBER_AVAILABLE:
        try:
            print("   📄 Trying pdfplumber extraction...")
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                        print(f"      ✅ Extracted page {page_num}: {len(page_text)} chars")
            
            if text.strip():
                print(f"   ✅ pdfplumber: Successfully extracted {len(text)} characters")
                return clean_extracted_text(text)
        except Exception as e:
            print(f"   ⚠️ pdfplumber failed: {e}")
    
    # Method 2: Fallback to PyPDF2
    if PYPDF2_AVAILABLE and not text.strip():
        try:
            print("   📄 Trying PyPDF2 extraction...")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                    print(f"      ✅ Extracted page {page_num}: {len(page_text)} chars")
            
            if text.strip():
                print(f"   ✅ PyPDF2: Successfully extracted {len(text)} characters")
                return clean_extracted_text(text)
        except Exception as e:
            print(f"   ⚠️ PyPDF2 failed: {e}")
    
    # If we got here, extraction failed
    if not text.strip():
        raise ValueError(
            "Failed to extract text from PDF. The file may be:\n"
            "- Scanned images without OCR\n"
            "- Encrypted/password protected\n"
            "- Corrupted\n"
            "Please provide a text-based PDF or paste resume text manually."
        )
    
    return clean_extracted_text(text)


def clean_extracted_text(text: str) -> str:
    """
    Clean up extracted text by removing excessive whitespace and formatting issues.
    """
    # Remove multiple consecutive newlines
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove excessive spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def validate_resume_content(text: str) -> bool:
    """
    Basic validation to check if extracted text looks like a resume.
    
    Returns:
        True if text appears to be a valid resume
    """
    # Check minimum length (resumes should be at least 200 chars)
    if len(text) < 200:
        print(f"   ⚠️ Text too short ({len(text)} chars) - may not be a complete resume")
        return False
    
    # Check for common resume keywords (at least 2 should be present)
    resume_keywords = [
        'experience', 'education', 'skills', 'work', 'project',
        'degree', 'university', 'college', 'company', 'position',
        'responsibilities', 'achievements', 'email', 'phone'
    ]
    
    text_lower = text.lower()
    keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
    
    if keyword_count < 2:
        print(f"   ⚠️ Only {keyword_count} resume keywords found - may not be a resume")
        return False
    
    print(f"   ✅ Resume validation passed ({len(text)} chars, {keyword_count} keywords)")
    return True


def extract_resume_from_pdf(pdf_file, validate: bool = True) -> str:
    """
    Main function to extract and validate resume from PDF.
    
    Args:
        pdf_file: File-like object from Streamlit file_uploader
        validate: Whether to validate the extracted content
        
    Returns:
        Cleaned resume text
        
    Raises:
        ValueError: If extraction fails or validation fails
    """
    print("\n📄 Processing PDF resume...")
    print(f"   File name: {pdf_file.name}")
    print(f"   File size: {pdf_file.size} bytes")
    
    # Extract text
    text = extract_text_from_pdf(pdf_file)
    
    # Validate if requested
    if validate and not validate_resume_content(text):
        raise ValueError(
            "Extracted text doesn't appear to be a valid resume. "
            "Please check the file or paste your resume text manually."
        )
    
    return text


# Quick test function
if __name__ == "__main__":
    print("PDF Processor Test")
    print("=" * 50)
    print(f"PyPDF2 available: {PYPDF2_AVAILABLE}")
    print(f"pdfplumber available: {PDFPLUMBER_AVAILABLE}")
    
    if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
        print("\n❌ No PDF libraries installed!")
        print("Run: pip install PyPDF2 pdfplumber")
    else:
        print("\n✅ PDF processing ready!")
