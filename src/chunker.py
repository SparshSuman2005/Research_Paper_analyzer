def chunk_text(text,overlap=50 , chunk_size= 150):
    chunks=[]
    words = text.split()
    step = chunk_size - overlap
    for i in range(0 , len(words) , step):
        chunk = words[i:i + chunk_size]
        chunk="".join(chunk)
        chunks.append(chunk)

    for i in range(0, len(words), step):
        chunk = text[i : i+step]
        chunk = " ".join(chunk)
        chunks.append(chunk)

    print("Number of chunks:", len(chunks))

    print("\nFirst chunk:")
    print(chunks[0])
    return chunks

