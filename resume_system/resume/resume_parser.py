import PyPDF2
import docx
import os

def extract_text(file_path):
    """Safely extracts text from PDF and DOCX files."""
    if not os.path.exists(file_path):
        return ""

    try:
        if file_path.endswith('.pdf'):
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
            return text.strip()

        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs]).strip()

    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

    return ""