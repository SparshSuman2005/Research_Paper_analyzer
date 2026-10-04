import arxiv
import requests
from supabase_client import supabase
import re
from embedder import embed_chunk

BUCKET_NAME = "Reasearch_paper"

def clean_paper_filename(title):
    clean = title.strip()
    clean = re.sub(r'[\\/:*?"<>|]', '', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean + ".pdf"

def get_paper_name(paper):
    return clean_paper_filename(paper.title)

def get_storage_files():
    try:
        return supabase.storage.from_(BUCKET_NAME).list() or []
    except Exception as e:
        print(f"Error listing storage bucket: {e}")
        return []

def search_arxiv(query, max_results=6):
    client = arxiv.Client(page_size=max_results, delay_seconds=3, num_retries=3)
    search = arxiv.Search(query=query, max_results=max_results)
    
    storage_files = {f["name"] for f in get_storage_files()}
    results = []

    for paper in client.results(search):
        filename = get_paper_name(paper)
        authors = [a.name for a in paper.authors][:5]
        results.append({
            "title": paper.title.strip().replace("\n", " "),
            "filename": filename,
            "authors": authors,
            "summary": re.sub(r'\s+', ' ', paper.summary.strip())[:400] + "...",
            "full_summary": re.sub(r'\s+', ' ', paper.summary.strip()),
            "published": paper.published.strftime('%Y-%m-%d') if paper.published else "",
            "pdf_url": paper.pdf_url,
            "entry_id": paper.entry_id,
            "is_indexed": filename in storage_files
        })
    return results

def ingest_pdf(pdf_url, filename):
    storage_files = {f["name"] for f in get_storage_files()}
    already_in_storage = filename in storage_files

    if not already_in_storage:
        response = requests.get(pdf_url, timeout=45)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download PDF from {pdf_url}: status {response.status_code}")
        
        content_type = response.headers.get("content-type", "").lower()
        if "application/pdf" not in content_type and not pdf_url.endswith(".pdf"):
            raise RuntimeError(f"URL did not return a PDF file (got {content_type})")

        # Upload to Supabase storage bucket
        supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=response.content,
            file_options={"content_type": "application/pdf"}
        )

    # Embed and index chunks
    chunk_count = embed_chunk([filename])
    return {
        "filename": filename,
        "chunks_count": chunk_count,
        "already_existed": already_in_storage
    }

def downlaod_paper(query):
    client = arxiv.Client(page_size=3, delay_seconds=3, num_retries=3)
    search = arxiv.Search(query=query, max_results=3)
    existing_files = {f["name"] for f in get_storage_files()}
    titles = []

    for paper in client.results(search):
        current_title = get_paper_name(paper)
        if current_title in existing_files:
            continue

        try:
            res = ingest_pdf(paper.pdf_url, current_title)
            titles.append(current_title)
        except Exception as e:
            print(f"Error ingesting {current_title}: {e}")
            continue

    return titles

download_paper = downlaod_paper
