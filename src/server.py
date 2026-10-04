import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

# Ensure src directory is in sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from supabase_client import supabase
from downloader import search_arxiv, ingest_pdf, clean_paper_filename, get_paper_name, downlaod_paper, BUCKET_NAME
from embedder import embed_question, embed_chunk
from retrieve import search_vector, make_context
from prompt import generate_answer
from database import get_indexed_papers_summary, delete_paper_from_db

app = FastAPI(
    title="Research Paper Analyzer API",
    description="Vector RAG pipeline for arXiv scientific papers",
    version="1.0.0"
)

# CORS middleware for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 6

class IngestRequest(BaseModel):
    query: Optional[str] = None
    pdf_url: Optional[str] = None
    title: Optional[str] = None

class QueryRequest(BaseModel):
    question: str
    paper_filter: Optional[str] = None
    top_k: Optional[int] = 5

@app.get("/api/status")
def get_system_status():
    """Verify backend and database connectivity."""
    try:
        papers_summary = get_indexed_papers_summary()
        total_chunks = sum(p["chunk_count"] for p in papers_summary)
        has_gemini = bool(os.getenv("GOOGLE_API_KEY"))
        has_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
        
        return {
            "status": "online",
            "supabase_connected": has_supabase,
            "gemini_connected": has_gemini,
            "papers_count": len(papers_summary),
            "total_chunks": total_chunks,
            "embedding_model": "all-MiniLM-L6-v2 (384-d)",
            "generation_model": "Gemini Flash"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.get("/api/papers")
def list_indexed_papers():
    """Return list of papers currently indexed in the vector database."""
    try:
        summary = get_indexed_papers_summary()
        # Clean up display titles for presentation
        result = []
        for item in summary:
            filename = item["paper_name"]
            display_title = filename[:-4] if filename.endswith(".pdf") else filename
            result.append({
                "filename": filename,
                "title": display_title,
                "chunk_count": item["chunk_count"]
            })
        return {"papers": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list papers: {str(e)}")

@app.post("/api/search")
def search_papers(req: SearchRequest):
    """Search arXiv for research papers."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    try:
        results = search_arxiv(req.query.strip(), max_results=req.max_results or 6)
        return {"results": results, "query": req.query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"arXiv search failed: {str(e)}")

@app.post("/api/ingest")
def ingest_paper(req: IngestRequest):
    """Download, extract, chunk, and embed a research paper."""
    try:
        # Case 1: Specific paper provided via pdf_url and title
        if req.pdf_url and req.title:
            filename = clean_paper_filename(req.title)
            res = ingest_pdf(req.pdf_url, filename)
            return {
                "success": True,
                "filename": filename,
                "title": req.title,
                "chunks_count": res.get("chunks_count", 0),
                "already_existed": res.get("already_existed", False),
                "message": f"Successfully indexed '{req.title}' ({res.get('chunks_count', 0)} chunks)"
            }
        
        # Case 2: Ingest from query string
        elif req.query and req.query.strip():
            titles = downlaod_paper(req.query.strip())
            if not titles:
                return {
                    "success": False,
                    "message": "No new papers downloaded (may already be indexed or no results found)."
                }
            return {
                "success": True,
                "indexed_papers": titles,
                "message": f"Successfully indexed {len(titles)} paper(s): {', '.join(titles)}"
            }
        else:
            raise HTTPException(status_code=400, detail="Either (pdf_url + title) or query must be supplied.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/query")
def answer_question(req: QueryRequest):
    """Embed query, retrieve pgvector chunks, and generate grounded answer with Gemini."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # 1. Embed user question
        query_vector = embed_question(req.question.strip())
        
        # 2. Retrieve nearest vector chunks
        matches = search_vector(
            query=query_vector,
            no=req.top_k or 5,
            paper_filter=req.paper_filter
        )
        
        if not matches:
            return {
                "question": req.question,
                "answer": "No indexed content matches your question. Please ensure relevant papers are ingested.",
                "sources": [],
                "paper_filter": req.paper_filter
            }

        # 3. Build grounding context
        context = make_context(matches)
        
        # 4. Generate answer via Gemini
        answer = generate_answer(req.question.strip(), context)
        
        # 5. Format sources for UI
        formatted_sources = []
        for idx, match in enumerate(matches, start=1):
            paper_name = match.get("paper_name", "")
            display_title = paper_name[:-4] if paper_name.endswith(".pdf") else paper_name
            sim = match.get("similarity")
            similarity_pct = round(float(sim) * 100, 1) if sim is not None else None
            
            formatted_sources.append({
                "source_num": idx,
                "paper_name": paper_name,
                "paper_title": display_title,
                "chunk_text": match.get("chunk_text", "").strip(),
                "similarity": sim,
                "similarity_pct": similarity_pct
            })
            
        return {
            "question": req.question,
            "answer": answer,
            "sources": formatted_sources,
            "paper_filter": req.paper_filter
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.delete("/api/papers/{paper_name}")
def delete_paper(paper_name: str):
    """Delete a paper's chunks from Supabase and remove PDF from storage."""
    try:
        # 1. Delete rows from database
        delete_paper_from_db(paper_name)
        
        # 2. Delete file from storage bucket
        try:
            supabase.storage.from_(BUCKET_NAME).remove([paper_name])
        except Exception as storage_err:
            print(f"Warning: Failed to delete file from storage: {storage_err}")
            
        return {
            "success": True,
            "message": f"Paper '{paper_name}' successfully removed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete paper: {str(e)}")

# Mount static files
static_dir = current_dir / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "PaperMind API is running. Static files are not yet created."}
