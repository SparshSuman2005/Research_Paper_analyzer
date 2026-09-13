import arxiv
import os
import requests
from supabase_client import supabase

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

    client = arxiv.Client()
    search = arxiv.Search(query=query,
    max_results=3)


    result = client.results(search)
    
    for paper in result:

        title = get_paper_name(paper)
        paper_exists=False
        for file in files:
            if file["name"]==title:
                paper_exists=True
                break

        if paper_exists:
            continue
        


        paper_id = paper.get_short_id()
        response = requests.get(paper.pdf_url,timeout=30)
        if response.get_status()!=200:
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
            path=title,
            file = response.content,
            file_options={
                "content_type" : "application/pdf"
            }
        )





            


        

    #     if not os.path.exists(f"../papers/{paper_id}.pdf"):

    #         response = requests.get(paper.pdf_url)

    #         with open(f"../papers/{paper_id}.pdf","wb")as file:
    #             file.write(response.content)
    #     else:
    #         print("Paper already there")

    # return
