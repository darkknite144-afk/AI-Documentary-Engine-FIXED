import httpx
from typing import List, Dict, Any
from app.search.base import SearchProvider
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class TavilyProvider(SearchProvider):
    def __init__(self):
        self.api_key = settings.tavily_api_key
        self.base_url = "https://api.tavily.com/search"
        self.enabled = bool(self.api_key)
        if self.enabled:
            logger.info("Tavily Search enabled.")
        else:
            logger.warning("Tavily Search API key missing. Provider disabled.")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced"
        }
        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "source": item.get("url", "")
                })
            return results
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            return []

    def health_check(self) -> bool:
        return self.enabled
