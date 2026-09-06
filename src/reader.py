import pypdf
import os

def read_text():

    text = ""
    folder_path="../papers"


    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            file_path = os.path.join(folder_path , file)
            
            for page in (pypdf.PdfReader(file_path)).pages:

                page_text=page.extract_text()

                if page_text:
                    text+=page_text

    return text        