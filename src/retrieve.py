from supabase_client import supabase

def search_vector(query , no = 5):
    response=supabase.rpc(
        "match_chunks",
        {
            "query_embedding":query,
            "match_count":no
        }
    ).execute()

    return response.data

def make_context(chunks):
    context=""

    for i , chunk in enumerate(chunks,start=1):
        context+=f"""
        source{i}
        Paper:{chunk['paper_name']}
        {chunk['chunk_text']}
        """

    return context

