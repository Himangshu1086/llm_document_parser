import nltk
from nltk.stem import WordNetLemmatizer
import re
from app.lib.constants.constants import constants
lemmatizer = WordNetLemmatizer()




def split_text_into_chunks(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks of approximately equal size.
    """
    chunks = []
    start = 0
    
    while start < len(text):
        # Find the end of the chunk
        end = start + chunk_size
        
        # If we're not at the end of the text, try to find a good breaking point
        if end < len(text):
            # Look for the last period or newline in the chunk
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            
            if break_point > start:
                end = break_point + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return chunks 



def get_summary_length(summary_length):
    return constants['SUMMARY_LENGTH'][summary_length]


def normalize_query(query):
    try:
        """Normalize the query: lowercase, remove punctuation, tokenize, stem and lemmatize words."""
        # Convert to lowercase
        query = query.lower()  
        
        # Remove punctuation
        query = re.sub(r'[^\w\s]', '', query)
        
        # Tokenize
        tokens = nltk.word_tokenize(query)
        
        # Stem words
        porter = nltk.PorterStemmer()
        stemmed_words = [porter.stem(word) for word in tokens]
        
        # Lemmatize stemmed words
        lemmatized_words = [lemmatizer.lemmatize(word) for word in stemmed_words if word not in [ 'is', 'the', 'i']]
        
        return " ".join(lemmatized_words)
    except Exception as e:
        print("Error normalizing query:", e)
        return query
