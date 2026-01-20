"""
SocialData.tools adapter for X (Twitter) data.
Provides a high-quality, cost-effective alternative to the official X API.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from app.adapters.base import SocialMediaAdapter, SocialPost

class SocialDataAdapter(SocialMediaAdapter):
    """
    Adapter for SocialData.tools API.
    A payload-efficient way to get real-time X data.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key or os.getenv("SOCIALDATA_API_KEY")
        self.base_url = "https://api.socialdata.tools/twitter"
    
    async def fetch_posts(
        self,
        query: str,
        max_results: int = 20,
        **kwargs
    ) -> List[SocialPost]:
        """
        Fetch real tweets via SocialData.tools.
        """
        if not self.api_key or self.api_key == "your_socialdata_key_here":
            print("⚠️ SocialData API Key missing. Skipping...")
            return []

        # The base URL is https://api.socialdata.tools
        # The endpoint for search according to documentation and SDKs is /twitter/search
        url = f"{self.base_url}" if self.base_url.endswith("/search") else f"{self.base_url}/search"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "SocialDataSDK/Python 1.0.0"
        }
        
        # SocialData expects 'query' and 'type' (Latest or Top)
        params = {
            "query": query,
            "type": "Latest"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    status = response.status
                    text = await response.text()
                    
                    if status == 200:
                        data = json.loads(text)
                        # SocialData returns a 'tweets' array
                        raw_tweets = data.get("tweets", [])
                        print(f"✅ SocialData: Successfully fetched {len(raw_tweets)} tweets for '{query}'")
                        return [self.normalize_post(t) for t in raw_tweets[:max_results]]
                    elif "Deprecated" in text:
                        print(f"❌ SocialData API Error: Endpoint '{url}' is deprecated. Please check for a new endpoint in the dashboard.")
                        return []
                    else:
                        print(f"❌ SocialData API Error: {status} - {text}")
                        return []
            except Exception as e:
                print(f"❌ SocialData Exception: {str(e)}")
                return []

    def normalize_post(self, raw_post: Dict[str, Any]) -> SocialPost:
        """
        Maps SocialData.tools JSON structure to our standard SocialPost
        """
        user = raw_post.get("user", {})
        
        return SocialPost(
            id=str(raw_post.get("id_str")),
            text=raw_post.get("full_text") or raw_post.get("text", ""),
            author_id=str(user.get("id_str")),
            author_username=user.get("screen_name", "unknown"),
            created_at=datetime.strptime(raw_post["created_at"], "%a %b %d %H:%M:%S %z %Y"),
            likes=raw_post.get("favorite_count", 0),
            retweets=raw_post.get("retweet_count", 0),
            replies=raw_post.get("reply_count", 0),
            language=raw_post.get("lang"),
            hashtags=[h["text"] for h in raw_post.get("entities", {}).get("hashtags", [])],
            raw_data=raw_post
        )

    async def validate_credentials(self) -> bool:
        return bool(self.api_key and self.api_key != "your_socialdata_key_here")

    @property
    def platform_name(self) -> str:
        return "socialdata"
