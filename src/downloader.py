import arxiv
import os

def downlaod_paper(query):

    client = arxiv.Client()
    search = arxiv.Search(query=query)


    result = client.results(search)
    if(result==null):
        print("No such paper exits ")
        return 0 

    if not os.path.exists(f"../papers/{query}.pdf"):
     paper.download_pdf(
        dirpath="../papers",
        filename=f"{query}.pdf"
    )
    else:
     print("Paper already there")

    


    
       
        

