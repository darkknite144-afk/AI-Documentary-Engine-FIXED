import httpx
from typing import List, Dict, Any
from app.search.base import SearchProvider
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class BraveSearchProvider(SearchProvider):
    def __init__(self):
        self.api_key = settings.brave_search_api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.enabled = bool(self.api_key)
        if self.enabled:
            logger.info("Brave Search enabled.")
        else:
            logger.warning("Brave Search API key missing. Provider disabled.")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": max_results
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "source": item.get("url", "")
                })
            return results
        except Exception as e:
            logger.error(f"Brave search failed: {str(e)}")
            return []

    def health_check(self) -> bool:
        return self.enabled
