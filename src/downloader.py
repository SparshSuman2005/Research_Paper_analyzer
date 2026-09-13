import arxiv
import os
import requests
from supabase_client import supabase
import re
from embedder import embed_chunk

files = (
    supabase
    .storage
    .from_("research_paper")
    .list()
    )



def get_paper_name(paper):

    title = paper.title.strip()

    title = re.sub(r'[\\/:*?"<>|]', '', title)

    title = re.sub(r'\s+', ' ', title)

    return title + ".pdf"

def downlaod_paper(query):

    client = arxiv.Client(
    page_size=3,
    delay_seconds=5,
    num_retries=5
    )
    search = arxiv.Search(query=query,
    max_results=3)
    title=[]


    result = client.results(search)
    
    for paper in result:

        current_title = get_paper_name(paper)
        paper_exists=False
        for file in files:
            if file["name"]==current_title:
                paper_exists=True
                break

        if paper_exists:
            continue
        


        response = requests.get(paper.pdf_url,timeout=30)
        if response.status_code!=200:
            print("no response from website ")  
            break
        application_type=response.headers.get(
            "content-type",
            ""
        ).lower()
        if "application/pdf" not in application_type:
            print("not an pdf but an html page")
            break
        

        #upload to the bucket 
        supabase.storage.from_("research_paper").upload(
            path=current_title,
            file = response.content,
            file_options={
                "content_type" : "application/pdf"
            }
        )
        title.append(current_title)

    embed_chunk(title)
    
