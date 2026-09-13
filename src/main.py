from downloader import downlaod_paper
from embedder import embed_question
from retrieve import search_vector,make_context
from prompt import generate_answer

name = input("Enter the name of the paper: ")
downlaod_paper(name)


question=""

while True:
    question = input("what is your question or type No Question : ")
    if question == "No Question":
        break
    query = embed_question(question)
    context = make_context(search_vector(query))
    answer = generate_answer(
        question,
        context
    )
    print(answer)

