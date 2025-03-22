# ------------------------------------------------------------ # ----------------------------------------

import os
import fitz  # PyMuPDF 
import faiss 
import numpy as np 
from flask import Flask, request, jsonify 
import openai 
import hashlib

from app.config.environment import EnvironmentVariables, config

# Set your OpenAI API key
openai.api_key = config[EnvironmentVariables.OPENAI_API_KEY.value]

# Global cache dictionary to store query results
cache = {}



# ------------------------------
# Ingestion & Indexing Functions
# ------------------------------

def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages in a PDF document."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text(text, max_chunk_size=500):
    """Splits text into chunks of maximum size (in characters)."""
    # A naive approach: split by newlines, then join until max_chunk_size is reached.
    lines = text.split('\n')
    chunks = []
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) < max_chunk_size:
            current_chunk += " " + line
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def get_embedding(text):
    """Generate an embedding for a given text using OpenAI's API."""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"  # Choose the embedding model
    )
    embedding = response['data'][0]['embedding']
    return np.array(embedding, dtype=np.float32)

def build_index(pdf_paths):
    """Builds a FAISS index for a list of PDF paths."""
    embeddings = []
    texts = []
    for pdf_path in pdf_paths:
        text = extract_text_from_pdf(pdf_path)
        chunks = split_text(text)
        for chunk in chunks:
            embedding = get_embedding(chunk)
            embeddings.append(embedding)
            texts.append(chunk)
    embeddings = np.array(embeddings)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, texts, embeddings

# ------------------------------
# Semantic Search & Summarization
# ------------------------------

def semantic_search(query, index, texts, embeddings, top_k=1):
    """Searches for the most relevant text chunk for a given query."""
    query_embedding = get_embedding(query)
    query_embedding = np.expand_dims(query_embedding, axis=0)
    distances, indices = index.search(query_embedding, top_k)
    best_match_idx = indices[0][0]
    return texts[best_match_idx], distances[0][0]

def summarize_text(text, summary_length="short"):
    """Uses an LLM to generate a summary of a given text."""
    # Adjust the prompt based on desired summary length
    prompt = f"Summarize the following text in a {summary_length} summary, retaining key technical details:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or another model like Claude or Llama 3 if available
        messages=[
            {"role": "system", "content": "You are a helpful summarization assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )
    summary = response['choices'][0]['message']['content'].strip()
    return summary

def process_query(query, index, texts, embeddings, summary_length="short", length_threshold=300):
    """Processes a user query, returning either the direct passage or a summary."""
    # Use caching to avoid duplicate LLM calls.
    cache_key = hashlib.sha256((query+summary_length).encode()).hexdigest()
    if cache_key in cache:
        return cache[cache_key]

    retrieved_text, distance = semantic_search(query, index, texts, embeddings)
    
    # If the text is too long, summarize it.
    if len(retrieved_text) > length_threshold:
        result = summarize_text(retrieved_text, summary_length=summary_length)
    else:
        result = retrieved_text

    # Cache the result.
    cache[cache_key] = result
    return result

# ------------------------------
# Flask API
# ------------------------------

app = Flask(__name__)

# Load and index PDF documents on startup.
# Replace with your PDF file paths.
pdf_paths = ["./assets/financial_doc.pdf"]
index, texts, embeddings = build_index(pdf_paths)

print("index: ", index)
print("texts: ", texts)
print("embeddings: ", embeddings)

@app.route("/query", methods=["POST"])
def query_endpoint():
    data = request.get_json()
    user_query = data.get("query", "")
    summary_length = data.get("summary_length", "short")
    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    result = process_query(user_query, index, texts, embeddings, summary_length=summary_length)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
