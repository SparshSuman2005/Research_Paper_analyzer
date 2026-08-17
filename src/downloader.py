import arxiv
import os 
from Pathlib import Path 

result = search_paper()
downloadpapers(result)




def downloadpapers(result):

    papers_folder= Path(__file__).parent.parent/"papers"
    papers_folder.mkdir(exist_ok=True)


    for papers in result:
        paper_id = papers.get_short_id()
        file_path = papers_folder/f"{paper_id}.pdf"


        if(file_path.exists()):
            print("Already Downloaded")
            continue

        print("downloading paper")

        papers.download_pdf(
            dirpath=papers_folder,
            filename = f"{paper_id}.pdf"
        )
        print("paper downloaded")


def search_paper():

    name = input("Enter the name of the paper : ")

    
    search = arxiv.Search(query=name , max_results=3)
    client = arxiv.Client()
    result = list(client.results(search))

    return result

        



