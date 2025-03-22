import openai
from app.config.environment import config, EnvironmentVariables
import numpy as np
import faiss
import pickle
import os
from app.lib.interfaces.global_error import GlobalError
from app.lib.enums.http_status_code import HttpStatusCode


openai.api_key = config[EnvironmentVariables.OPENAI_API_KEY.value]

def generate_embeddings(text_chunks, document_id):
    try:
        embeddings = []
        for chunk in text_chunks:
            response = openai.Embedding.create(
                input=chunk,
                model="text-embedding-ada-002"
            )
            embeddings.append(response['data'][0]['embedding'])
    
        # Store embeddings and text chunks
        store_embeddings(embeddings, text_chunks, document_id)
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", 
                           status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, 
                           error=e).to_dict()



def store_embeddings(embeddings, text_chunks, document_id):
    try:
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Get the existing index or create a new one
        index_path = 'uploads/faiss_index'
        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
        else:
            index = faiss.IndexFlatL2(len(embeddings_array[0]))
        
        # Add the new embeddings to the index
        index.add(embeddings_array)
        
        # Save the updated index
        faiss.write_index(index, index_path)
        
        # Store the text chunks with their document ID
        chunks_path = 'uploads/text_chunks.pkl'
        chunks_data = {}
        if os.path.exists(chunks_path):
            with open(chunks_path, 'rb') as f:
                chunks_data = pickle.load(f)
        
        chunks_data[document_id] = text_chunks
        
        with open(chunks_path, 'wb') as f:
            pickle.dump(chunks_data, f) 
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", 
                           status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, 
                           error=e).to_dict()
