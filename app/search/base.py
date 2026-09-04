from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SearchProvider(ABC):
    """Abstract base class for all search providers."""
    
    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Execute a search and return normalized results."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if this provider is configured and ready."""
        pass
