from typing import List, Dict, Any
from app.search.base import SearchProvider
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class DuckDuckGoProvider(SearchProvider):
    def __init__(self):
        self.enabled = True
        logger.info("DuckDuckGo provider enabled (no API key required).")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.error("duckduckgo_search not installed.")
            return []

        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", r.get("url", "")),
                        "snippet": r.get("body", r.get("snippet", "")),
                        "source": r.get("href", "")
                    })
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
        return results

    def health_check(self) -> bool:
        return self.enabled
