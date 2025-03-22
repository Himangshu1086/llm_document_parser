import fitz
from app.services.embeddings_service import generate_embeddings
from app.utils.text_utils import split_text_into_chunks
import os
from app.lib.interfaces.global_error import GlobalError
from app.lib.enums.http_status_code import HttpStatusCode

def process_document(file):
    # Save the file temporarily
    temp_path = os.path.join('uploads', file.filename)
    file.save(temp_path)

    try:
        # Extract text from PDF
        doc = fitz.open(temp_path)
        text = ""
        for page in doc:
            text += page.get_text()

        # Split text into chunks
        chunks = split_text_into_chunks(text)

        # Generate embeddings for chunks
        generate_embeddings(chunks, file.filename)
    except Exception as e:
        os.remove(temp_path)
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()

    finally:
        # Clean up
        os.remove(temp_path) 