from supabase_client import supabase

def search_vector(query, no=5, paper_filter=None):
    # If a specific paper is selected, request more candidates to ensure sufficient paper-specific matches
    fetch_count = no * 4 if paper_filter else no
    response = supabase.rpc(
        "match_chunks",
        {
            "query_embedding": query,
            "match_count": fetch_count
        }
    ).execute()

    results = response.data or []
    if paper_filter:
        filtered = [r for r in results if r.get("paper_name") == paper_filter]
        results = filtered[:no] if filtered else results[:no]

    return results

def make_context(chunks):
    if not chunks:
        return "No relevant context found in the indexed papers."

    context_parts = []
    for i, chunk in enumerate(chunks, start=1):
        paper = chunk.get("paper_name", "Unknown Paper")
        text = chunk.get("chunk_text", "").strip()
        similarity = chunk.get("similarity")
        score_info = f" (relevance: {similarity:.2f})" if similarity is not None else ""
        context_parts.append(f"[Source {i}: {paper}{score_info}]\n{text}")

    return "\n\n---\n\n".join(context_parts)


