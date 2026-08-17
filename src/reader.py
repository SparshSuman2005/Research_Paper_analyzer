import arxiv


name=input("Enter the name of the paper : ")
top_n = int(input("Enter the number of the paper : "))

search = arxiv.Search(query=name , max_results=top_n)

client = arxiv.Client()

results = client.results(search)
results=list(results)


for paper in results:
    print("\nTitle : " , paper.title )
    print("\nAuthor : ",", ".join(author.name for author in paper.authors))
    print("\nPublished : " , paper.published)
    print("\nArXiv ID : ", paper.entry_id)
    print("\nPDF URL : ",paper.pdf_url)


