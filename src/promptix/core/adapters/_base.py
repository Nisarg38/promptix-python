from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ModelAdapter(ABC):
    """Base adapter class for different model providers."""
    
    @abstractmethod
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt the configuration for specific provider."""
        pass

    @abstractmethod
    def adapt_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Adapt message format for specific provider."""
        pass 