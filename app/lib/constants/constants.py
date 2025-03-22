

constants = {
    "TEXT_CHUNKS_FILE": "text_chunks.pkl",
    "INDEX_DIR": "uploads/",
    "INDEX_NAME": "faiss_index",
    "OPENAI_EMBEDDING_MODEL": "text-embedding-ada-002",
    "OPENAI_SUMMARIZATION_MODEL": "gpt-3.5-turbo",
    'THRESHOLD_DISTANCE': 0.3,  # distance upto which the retrieved_text is clear
    'SUMMARY_LENGTH': {
        'short': 100,
        'medium': 200,
        'long': 300
    }
}