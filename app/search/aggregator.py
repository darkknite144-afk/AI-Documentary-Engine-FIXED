import urllib.parse
from typing import List, Dict, Any
from app.search.duckduckgo import DuckDuckGoProvider
from app.search.tavily import TavilyProvider
from app.search.brave import BraveSearchProvider
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class SearchAggregator:
    def __init__(self):
        # Free-first priority: Tavily -> Brave -> DuckDuckGo.
        # Brave and Tavily are only "active" if their API key is configured;
        # DuckDuckGo needs no key so it is always available as a baseline.
        self.providers = [
            TavilyProvider(),
            BraveSearchProvider(),
            DuckDuckGoProvider()
        ]
        self.active_providers = [p for p in self.providers if p.health_check()]

    def normalize_url(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.replace('www.', '')
            path = parsed.path.rstrip('/')
            return f"{parsed.scheme}://{netloc}{path}".lower()
        except Exception:
            return url.lower()

    def filter_junk_sources(self, results: List[Dict[str, Any]], original_query: str) -> List[Dict[str, Any]]:
        """Removes highly irrelevant domains and ensures basic query relevance."""
        blocked_domains = ['man.eu', 'man.com', 'dictionary.com', 'amazon.com', 'imdb.com']
        query_keywords = [w.lower() for w in original_query.split() if len(w) > 3]
        
        filtered = []
        for res in results:
            url = res.get('url', '').lower()
            title = res.get('title', '').lower()
            
            # 1. Block known junk domains
            if any(bd in url for bd in blocked_domains):
                continue
                
            # 2. Relevancy Check: At least one major keyword must be in URL or Title
            if query_keywords:
                relevance_match = any(kw in url or kw in title for kw in query_keywords)
                if not relevance_match:
                    continue
            
            filtered.append(res)
        return filtered

    def rank_and_deduplicate(self, all_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_urls = set()
        unique_results = []
        high_authority = ['.edu', '.gov', 'wikipedia.org', 'bbc.com', 'reuters.com', 'history.com']
        
        for res in all_results:
            raw_url = res.get('url', '')
            if not raw_url:
                continue
                
            norm_url = self.normalize_url(raw_url)
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                
                score = 1.0
                if any(domain in raw_url.lower() for domain in high_authority):
                    score += 2.0
                    
                res['authority_score'] = score
                unique_results.append(res)
        
        unique_results.sort(key=lambda x: x.get('authority_score', 0), reverse=True)
        return unique_results

    def execute_search(self, query: str, max_total_results: int = 10) -> List[Dict[str, Any]]:
        if not self.active_providers:
            logger.error("CRITICAL: No search providers active. Check Tavily key or DuckDuckGo status.")
            return []
            
        all_results = []
        # Query every active provider and merge results for source diversity
        # (a single provider's index can miss sources another one has).
        # rank_and_deduplicate() below removes duplicate URLs afterwards.
        for provider in self.active_providers:
            try:
                results = provider.search(query, max_results=max_total_results)
                if results:
                    all_results.extend(results)
            except Exception as e:
                logger.warning(f"Search provider {provider.__class__.__name__} failed: {str(e)}")
                
        filtered_results = self.filter_junk_sources(all_results, query)
        final_results = self.rank_and_deduplicate(filtered_results)
        
        logger.info(f"Aggregated {len(all_results)} raw results -> {len(final_results)} clean ranked links.")
        return final_results[:max_total_results]

search_aggregator = SearchAggregator()
