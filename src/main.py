from downloader import downlaod_paper
from reader import read_text
from chunker import chunk_text

name = input("Enter the name of the : ")
downlaod_paper(name)

chunk_text(read_text())




