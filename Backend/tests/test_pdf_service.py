import io
from pypdf import PdfWriter
from app.services.pdf_service import parse_pdf_to_text

def test_pdf_parsing():
    # Create a minimal empty PDF or test handling
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    stream = io.BytesIO()
    writer.write(stream)
    pdf_bytes = stream.getvalue()

    extracted = parse_pdf_to_text(pdf_bytes)
    assert isinstance(extracted, str)
