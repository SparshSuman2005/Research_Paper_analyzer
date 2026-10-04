from supabase_client import supabase

def insert_chunks(paper_name, chunk, vector):
    data = []
    for chunk_t, vector_e in zip(chunk, vector):
        data.append({
            "paper_name": paper_name,
            "chunk_text": chunk_t,
            "embeddings": vector_e
        })
    
    # Insert in batches of 100 to avoid payload limits
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        supabase.table("chunks").insert(batch).execute()
    return len(data)

def get_indexed_papers_summary():
    """Retrieve distinct papers with their chunk counts."""
    response = supabase.table("chunks").select("paper_name").execute()
    counts = {}
    for row in (response.data or []):
        name = row.get("paper_name")
        if name:
            counts[name] = counts.get(name, 0) + 1
    
    return [{"paper_name": name, "chunk_count": count} for name, count in sorted(counts.items())]

def delete_paper_from_db(paper_name):
    """Delete chunks belonging to a paper from the chunks table."""
    return supabase.table("chunks").delete().eq("paper_name", paper_name).execute()

