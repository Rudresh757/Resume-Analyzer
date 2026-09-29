import io
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def parse_pdf_to_text(pdf_bytes: bytes) -> str:
    """
    Extract readable text from a PDF file buffer using pypdf.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
        result = "\n".join(extracted_pages).strip()
        logger.info(f"Successfully extracted {len(result)} characters from PDF.")
        return result
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise ValueError(f"Failed to parse PDF document: {str(e)}")

async def generate_pdf_from_html(html_content: str) -> bytes:
    """
    Convert HTML content into high-quality PDF bytes using Playwright.
    Attempts system Chrome first, then Edge, then default Chromium.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = None
        # Try system installed Chrome or Edge first (instant, no download needed)
        for channel in ["chrome", "msedge", None]:
            try:
                launch_kwargs = {"headless": True}
                if channel:
                    launch_kwargs["channel"] = channel
                browser = await p.chromium.launch(**launch_kwargs)
                break
            except Exception as launch_err:
                logger.debug(f"Could not launch browser with channel={channel}: {launch_err}")

        if browser is None:
            raise RuntimeError(
                "Could not launch any Chromium-based browser (Chrome, Edge, or Playwright Chromium). "
                "Please make sure Google Chrome or Microsoft Edge is installed."
            )

        try:
            page = await browser.new_page()
            await page.set_content(html_content, wait_until="load")
            pdf_bytes = await page.pdf(
                format="A4",
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm"
                },
                print_background=True
            )
            return pdf_bytes
        finally:
            await browser.close()
