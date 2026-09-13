import pypdf
import io
from dotenv import load_dotenv
from supabase_client import supabase


def read_text(file):

    text = ""
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