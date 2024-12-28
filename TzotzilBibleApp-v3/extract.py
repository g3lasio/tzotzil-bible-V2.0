import os
import pdfplumber


def extract_text_from_pdfs(directory):
    documents = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf"):
                path = os.path.join(root, file)
                with pdfplumber.open(path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text()
                documents[file] = text
    return documents


# Ejemplo de uso
theology_path = "Theology"
docs = extract_text_from_pdfs(theology_path)
