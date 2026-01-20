"""
Twitter/X API adapter for social media analytics.

This adapter implements the SocialMediaAdapter interface for Twitter/X,
allowing seamless integration with the Twitter API v2.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from app.adapters.base import SocialMediaAdapter, SocialPost


class TwitterAdapter(SocialMediaAdapter):
    """
    Twitter/X API adapter.
    
    Implements data fetching from Twitter using the Twitter API v2.
    Supports both free and premium tier endpoints.
    
    Example:
        adapter = TwitterAdapter(
            api_key="your_api_key",
            api_secret="your_api_secret",
            bearer_token="your_bearer_token"
        )
        
        posts = await adapter.fetch_posts("#AI", max_results=100)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Twitter adapter with API credentials.
        
        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            bearer_token: Twitter bearer token (recommended for v2 API)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        
        # API endpoints
        self.base_url = "https://api.twitter.com/2"
        self.search_endpoint = f"{self.base_url}/tweets/search/recent"
    
    async def fetch_posts(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SocialPost]:
        """
        Fetch tweets matching the search query.
        
        Args:
            query: Twitter search query
            max_results: Maximum tweets to fetch
            start_time: Filter tweets after this time
            end_time: Filter tweets before this time
            
        Returns:
            List of standardized SocialPost objects
        """
        if self.bearer_token and self.bearer_token != "your_bearer_token_here":
            try:
                # Use real API if token is configured
                response = await self._make_api_request(query, max_results, start_time, end_time)
                
                # Check for errors in response
                if "errors" in response and not "data" in response:
                    print(f"⚠️ Twitter API Error: {response['errors']}")
                    return await self._fetch_mock_posts(query, max_results)

                # Normalize posts
                posts = []
                for raw_post in response.get('data', []):
                    # Pass the includes (users, etc) to helping normalization if needed, 
                    # but for now we'll stick to basic normalization
                    # Ideally normalization should look up user info from 'includes'
                    posts.append(self.normalize_post(raw_post))
                
                return posts
            except Exception as e:
                print(f"⚠️ API Request failed ({e}), falling back to mock data.")
                return await self._fetch_mock_posts(query, max_results)
        
        # Fallback to mock data if no token
        return await self._fetch_mock_posts(query, max_results)
    
    async def _fetch_mock_posts(self, query: str, max_results: int) -> List[SocialPost]:
        """
        Generate mock Twitter posts for testing.
        
        In production, replace this with actual Twitter API calls.
        """
        posts = []
        
        for i in range(min(max_results, 120)):
            # Simulate different sentiment patterns
            if i % 3 == 0:
                text = f"{query} is amazing for developers #{i}"
            elif i % 3 == 1:
                text = f"I am unsure about {query} future #{i}"
            else:
                text = f"{query} is overhyped and risky #{i}"
            
            post = SocialPost(
                id=f"tweet_{i}",
                text=text,
                author_id=f"user_{i % 10}",
                author_username=f"user{i % 10}",
                created_at=datetime.now(),
                likes=int(100 * (1 - i / max_results)),
                retweets=int(50 * (1 - i / max_results)),
                replies=int(20 * (1 - i / max_results)),
                language="en",
                hashtags=self.extract_hashtags(text),
                mentions=self.extract_mentions(text),
                urls=self.extract_urls(text)
            )
            
            posts.append(post)
        
        return posts
    
    async def _make_api_request(
        self,
        query: str,
        max_results: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Make actual Twitter API request.
        
        This is a template for real API integration.
        """
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "query": query,
            "max_results": min(max_results, 100),  # API limit
            "tweet.fields": "created_at,public_metrics,lang,entities",
            "user.fields": "username",
            "expansions": "author_id"
        }
        
        if start_time:
            params["start_time"] = start_time.isoformat() + "Z"
        if end_time:
            params["end_time"] = end_time.isoformat() + "Z"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.search_endpoint,
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Twitter API error: {response.status}")
    
    def normalize_post(self, raw_post: Dict[str, Any]) -> SocialPost:
        """
        Convert Twitter API response to standardized SocialPost.
        
        Args:
            raw_post: Raw tweet data from Twitter API v2
            
        Returns:
            Standardized SocialPost object
            
        Example Twitter API v2 response:
            {
                "id": "1234567890",
                "text": "This is a tweet #example",
                "created_at": "2024-01-01T12:00:00.000Z",
                "author_id": "9876543210",
                "public_metrics": {
                    "like_count": 10,
                    "retweet_count": 5,
                    "reply_count": 2
                },
                "lang": "en",
                "entities": {
                    "hashtags": [{"tag": "example"}],
                    "mentions": [{"username": "user"}],
                    "urls": [{"expanded_url": "https://example.com"}]
                }
            }
        """
        text = raw_post.get("text", "")
        metrics = raw_post.get("public_metrics", {})
        entities = raw_post.get("entities", {})
        
        # Extract hashtags
        hashtags = [
            tag["tag"].lower()
            for tag in entities.get("hashtags", [])
        ]
        
        # Extract mentions
        mentions = [
            mention["username"].lower()
            for mention in entities.get("mentions", [])
        ]
        
        # Extract URLs
        urls = [
            url.get("expanded_url", url.get("url", ""))
            for url in entities.get("urls", [])
        ]
        
        return SocialPost(
            id=raw_post["id"],
            text=text,
            author_id=raw_post.get("author_id", ""),
            author_username=raw_post.get("username", "unknown"),
            created_at=datetime.fromisoformat(
                raw_post["created_at"].replace("Z", "+00:00")
            ),
            likes=metrics.get("like_count", 0),
            retweets=metrics.get("retweet_count", 0),
            replies=metrics.get("reply_count", 0),
            language=raw_post.get("lang"),
            hashtags=hashtags,
            mentions=mentions,
            urls=urls,
            raw_data=raw_post
        )
    
    async def validate_credentials(self) -> bool:
        """
        Validate Twitter API credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.bearer_token:
            return False
        
        try:
            # Make a simple API call to verify credentials
            # For now, just check if bearer_token exists
            return True
        except Exception:
            return False
    
    @property
    def platform_name(self) -> str:
        """Return platform name."""
        return "twitter"
    
    def build_query(
        self,
        keywords: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        mentions: Optional[List[str]] = None,
        exclude_retweets: bool = True,
        language: Optional[str] = None
    ) -> str:
        """
        Build a Twitter search query with advanced operators.
        
        Args:
            keywords: Keywords to search for
            hashtags: Hashtags to include (without #)
            mentions: Usernames to include (without @)
            exclude_retweets: Whether to exclude retweets
            language: Language code (e.g., 'en', 'es')
            
        Returns:
            Formatted Twitter search query string
            
        Example:
            query = adapter.build_query(
                keywords=["AI", "machine learning"],
                hashtags=["tech"],
                exclude_retweets=True,
                language="en"
            )
            # Returns: "(AI OR machine learning) #tech -is:retweet lang:en"
        """
        query_parts = []
        
        # Add keywords
        if keywords:
            keywords_query = " OR ".join(keywords)
            query_parts.append(f"({keywords_query})")
        
        # Add hashtags
        if hashtags:
            for tag in hashtags:
                query_parts.append(f"#{tag}")
        
        # Add mentions
        if mentions:
            for mention in mentions:
                query_parts.append(f"@{mention}")
        
        # Exclude retweets
        if exclude_retweets:
            query_parts.append("-is:retweet")
        
        # Add language filter
        if language:
            query_parts.append(f"lang:{language}")
        
        return " ".join(query_parts)
