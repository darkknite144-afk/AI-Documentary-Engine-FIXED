import httpx
from bs4 import BeautifulSoup
from app.models.source import Source
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class WebFetcher:
    def fetch_content(self, source: Source) -> str:
        logger.info(f"Fetching content from: {source.url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(source.url, headers=headers)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            # Clean up excessive newlines
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)
            
            # Truncate to a reasonable length for the LLM context window
            return clean_text[:10000]
            
        except Exception as e:
            logger.error(f"Failed to fetch {source.url}: {str(e)}")
            return ""

web_fetcher = WebFetcher()
