def split_text_into_chunks(text, chunk_size=1000, overlap=100):
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