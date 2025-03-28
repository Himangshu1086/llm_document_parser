import faiss
import pickle
import openai
import numpy as np
from app.config.environment import config, EnvironmentVariables
from app.lib.interfaces.global_error import GlobalError
from app.lib.enums.http_status_code import HttpStatusCode
from app.lib.constants.constants import constants
from app.utils.text_utils import get_summary_length, normalize_query, get_summary_length, clean_text
from app.lib.enums.enums import SummaryLengthType
import hashlib



openai.api_key = config[EnvironmentVariables.OPENAI_API_KEY.value]

index = None
text_chunks = None

# in memory cache for search results
cache = {}

'''Initialize the search service on startup'''
def init_search_service():
    global index, text_chunks, cache
    try:
        index = faiss.read_index(constants.get('INDEX_DIR') + constants.get('INDEX_NAME'))
        with open(constants.get('INDEX_DIR') + constants.get('TEXT_CHUNKS_FILE'), 'rb') as f:
            text_chunks = pickle.load(f)

    except:
        index = None
        text_chunks = {}




'''Search for documents based on a query'''
def search_documents(query, summary_length_type=SummaryLengthType.SHORT.value, top_k_results=1):
    try:
        if index is None:
            return GlobalError(message="No documents indexed", 
                               status_code=HttpStatusCode.NOT_FOUND.value).to_dict()
        
        # Check cache first
        query_normalized = normalize_query(query + " " + summary_length_type)
        cache_key = hashlib.sha256((query_normalized).encode()).hexdigest()
        if cache_key in cache:
            return cache[cache_key]

        summary_length = get_summary_length(summary_length_type)


        # Generate query embedding
        query_embedding = openai.Embedding.create(
            input=query,
            model=constants.get('OPENAI_EMBEDDING_MODEL')
        )['data'][0]['embedding']

        # Search the index (considering top 1 match as of now)
        distances, indices = index.search(np.array([query_embedding])
                                          .astype('float32'),top_k_results)
        best_match_idx = indices[0][0]

        results = {}
               
        # Check if the passage is unclear based on distance and content
        distance = distances[0][0]  # Get the distance for current result
        retrieved_text = text_chunks[0][best_match_idx]


        if retrieved_text is None or distance > 0.7:
            # No results found → Ask LLM to generate a summary from the document
            document_text = " ".join(text_chunks[:5])  # Use first few chunks as context
            prompt = f"Answer the query '{query}' based on this document: {document_text}"
            result = summarize_text(prompt, summary_length)
            results = {'summary': result}
        else:
            is_unclear = (
                distance > constants.get('THRESHOLD_DISTANCE') or  # FAISS distance too high
                len(retrieved_text.split()) < 20 or  # Too short passage
                len(set(query.lower().split()) & 
                    set(retrieved_text.lower().split())) < 3  # Low keyword overlap
                    )     
                    
            if is_unclear or len(retrieved_text.split()) > summary_length:
                results = {
                    'text': clean_text(retrieved_text),
                    'summary': summarize_text(retrieved_text,query,summary_length)
                }
            else:
                results = {
                    'text': clean_text(retrieved_text)
                    }

        cache[cache_key] = results
        return results
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", 
                           status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, 
                           error=e).to_dict()





'''Summarize text using OpenAI'''
def summarize_text(text, query, summary_length):
    try:
        prompt = f"Summarize the following text in a {summary_length} words summary in context with the question {query}, retaining key technical details:\n\n{text}"
        response = openai.ChatCompletion.create(
            model=constants.get('OPENAI_MODEL'),
            messages=[
                {"role": "system", "content": "Summarize the following text concisely:"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'] 
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()
