"""
Base adapter interface for social media data ingestion.

This module defines the abstract interface that all social media adapters
must implement. It ensures consistency across different platforms and makes
it easy to add new data sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SocialPost:
    """
    Standardized social media post structure.
    
    All adapters must convert platform-specific posts into this format.
    """
    id: str
    text: str
    author_id: str
    author_username: str
    created_at: datetime
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    language: Optional[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    urls: List[str] = None
    raw_data: Optional[Dict[str, Any]] = None  # Original platform data
    
    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.urls is None:
            self.urls = []


class SocialMediaAdapter(ABC):
    """
    Abstract base class for social media data adapters.
    
    Each platform (Twitter, Reddit, LinkedIn, etc.) should implement this
    interface to provide a consistent way to fetch and process posts.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the adapter with authentication credentials.
        
        Args:
            api_key: API key for the platform
            **kwargs: Additional platform-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def fetch_posts(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SocialPost]:
        """
        Fetch posts from the platform based on a search query.
        
        Args:
            query: Search query (topic, hashtag, keyword, etc.)
            max_results: Maximum number of posts to fetch
            start_time: Filter posts after this time
            end_time: Filter posts before this time
            
        Returns:
            List of standardized SocialPost objects
        """
        pass
    
    @abstractmethod
    def normalize_post(self, raw_post: Dict[str, Any]) -> SocialPost:
        """
        Convert platform-specific post format to standardized SocialPost.
        
        Args:
            raw_post: Raw post data from the platform API
            
        Returns:
            Standardized SocialPost object
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that the API credentials are working.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text.
        
        Args:
            text: Post text content
            
        Returns:
            List of hashtags (without # symbol)
        """
        import re
        return [tag.lower() for tag in re.findall(r'#(\w+)', text)]
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract user mentions from text.
        
        Args:
            text: Post text content
            
        Returns:
            List of mentioned usernames (without @ symbol)
        """
        import re
        return [mention.lower() for mention in re.findall(r'@(\w+)', text)]
    
    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from text.
        
        Args:
            text: Post text content
            
        Returns:
            List of URLs
        """
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the name of the platform (e.g., 'twitter', 'reddit')."""
        pass
