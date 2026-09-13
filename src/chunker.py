def chunk_text(text,overlap=50 , chunk_size= 150):
    chunks=[]
    words = text.split()
    step = chunk_size - overlap
    for i in range(0 , len(words) , step):
        chunk = words[i:i + chunk_size]
        chunk=" ".join(chunk)
        chunks.append(chunk)
    return chunks