import arxiv
import os
import requests

def downlaod_paper(query):

    client = arxiv.Client()
    search = arxiv.Search(query=query,
    max_results=3)


    result = client.results(search)
    
    for paper in result:
        paper_id = paper.get_short_id()

        

        if not os.path.exists(f"../papers/{paper_id}.pdf"):

            response = requests.get(paper.pdf_url)

            with open(f"../papers/{paper_id}.pdf","wb")as file:
                file.write(response.content)
        else:
            print("Paper already there")

    return
