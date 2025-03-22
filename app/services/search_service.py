import faiss
import pickle
import openai
import numpy as np
from app.config.environment import config, EnvironmentVariables
from app.lib.interfaces.global_error import GlobalError
from app.lib.enums.http_status_code import HttpStatusCode
from app.lib.constants.constants import constants

openai.api_key = config[EnvironmentVariables.OPENAI_API_KEY.value]

index = None
text_chunks = None


def init_search_service():
    global index, text_chunks
    try:
        index = faiss.read_index(constants.get('INDEX_DIR') + constants.get('INDEX_NAME'))
        with open(constants.get('INDEX_DIR') + constants.get('TEXT_CHUNKS_FILE'), 'rb') as f:
            text_chunks = pickle.load(f)
    except:
        index = None
        text_chunks = {}


def search_documents(query, k=1):
    try:
        if index is None:
            return GlobalError(message="No documents indexed", status_code=HttpStatusCode.NOT_FOUND.value).to_dict()

        # Generate query embedding
        query_embedding = openai.Embedding.create(
            input=query,
            model=constants.get('OPENAI_EMBEDDING_MODEL')
        )['data'][0]['embedding']

        # Search the index
        distances, indices = index.search(np.array([query_embedding]).astype('float32'), k)
        
        # Get the corresponding text chunks
        results = []
        for idx in indices[0]:
            for doc_id, chunks in text_chunks.items():
                if idx < len(chunks):
                    results.append({
                        'document': doc_id,
                        'text': chunks[idx],
                        'summary': summarize_text(chunks[idx])
                    })

            return results
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()



def summarize_text(text):
    try:
        response = openai.ChatCompletion.create(
            model=constants.get('OPENAI_SUMMARIZATION_MODEL'),
            messages=[
                {"role": "system", "content": "Summarize the following text concisely:"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message['content'] 
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()
