import pypdf
import io
from dotenv import load_dotenv
from supabase import create_client
import os


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)
text = ""

def read_text(file):

    
    pdf_bytes = (
            supabase.
            storage
            .from_("research_paper")
            .download(file["name"])
        )
    
    pdf_file=io.BytesIO(pdf_bytes)
    reader=pypdf.PdfReader(pdf_file)
    
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text+=page_text

    return text        