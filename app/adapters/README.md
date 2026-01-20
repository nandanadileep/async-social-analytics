# Social Media Ingestion Adapter System

A pluggable adapter interface for ingesting data from multiple social media platforms.

## 📋 Overview

The adapter system provides a **clean, standardized interface** for fetching and processing social media data from different platforms. It's designed to be:

- **Platform-agnostic**: Easy to add new platforms
- **Type-safe**: Standardized data structures
- **Async-first**: Built for high-performance data fetching
- **Production-ready**: Includes error handling, validation, and normalization

## 🏗️ Architecture

```
app/adapters/
├── __init__.py
├── base.py          # Abstract base class & SocialPost dataclass
├── twitter.py       # Twitter/X implementation
├── factory.py       # Adapter factory & registry
└── README.md        # This file
```

### Core Components

1. **`SocialPost`** - Standardized post format
2. **`SocialMediaAdapter`** - Abstract base class
3. **`TwitterAdapter`** - Twitter implementation
4. **`AdapterFactory`** - Creates adapter instances

## 🚀 Quick Start

### Using the Twitter Adapter

```python
from app.adapters.factory import get_adapter

# Create adapter
adapter = get_adapter('twitter', bearer_token='your_token')

# Fetch posts
posts = await adapter.fetch_posts('#AI', max_results=100)

# Process posts
for post in posts:
    print(f"{post.author_username}: {post.text}")
    print(f"Likes: {post.likes}, Retweets: {post.retweets}")
```

### Advanced Query Building

```python
from app.adapters.twitter import TwitterAdapter

adapter = TwitterAdapter(bearer_token='your_token')

# Build complex query
query = adapter.build_query(
    keywords=["AI", "machine learning"],
    hashtags=["tech", "innovation"],
    exclude_retweets=True,
    language="en"
)

# Fetch with query
posts = await adapter.fetch_posts(query, max_results=100)
```

## 📊 SocialPost Structure

All adapters convert platform-specific data into this standardized format:

```python
@dataclass
class SocialPost:
    id: str                          # Unique post ID
    text: str                        # Post content
    author_id: str                   # Author's user ID
    author_username: str             # Author's username
    created_at: datetime             # Post timestamp
    likes: int                       # Number of likes
    retweets: int                    # Number of shares/retweets
    replies: int                     # Number of replies
    language: Optional[str]          # Language code (e.g., 'en')
    hashtags: List[str]              # Extracted hashtags
    mentions: List[str]              # Extracted @mentions
    urls: List[str]                  # Extracted URLs
    raw_data: Optional[Dict]         # Original platform data
```

## 🔌 Adding a New Platform

### Step 1: Create Adapter Class

```python
# app/adapters/reddit.py
from app.adapters.base import SocialMediaAdapter, SocialPost
from typing import List, Dict, Any
from datetime import datetime

class RedditAdapter(SocialMediaAdapter):
    
    async def fetch_posts(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SocialPost]:
        # Implement Reddit API calls
        pass
    
    def normalize_post(self, raw_post: Dict[str, Any]) -> SocialPost:
        # Convert Reddit post to SocialPost
        return SocialPost(
            id=raw_post['id'],
            text=raw_post['selftext'] or raw_post['title'],
            author_id=raw_post['author'],
            author_username=raw_post['author'],
            created_at=datetime.fromtimestamp(raw_post['created_utc']),
            likes=raw_post['score'],
            retweets=0,  # Reddit doesn't have retweets
            replies=raw_post['num_comments'],
            hashtags=[],
            mentions=[],
            urls=[],
            raw_data=raw_post
        )
    
    async def validate_credentials(self) -> bool:
        # Validate Reddit API credentials
        return True
    
    @property
    def platform_name(self) -> str:
        return "reddit"
```

### Step 2: Register Adapter

```python
# In app/adapters/factory.py or your initialization code
from app.adapters.factory import AdapterFactory
from app.adapters.reddit import RedditAdapter

AdapterFactory.register_adapter('reddit', RedditAdapter)
```

### Step 3: Use It!

```python
adapter = get_adapter('reddit', client_id='...', client_secret='...')
posts = await adapter.fetch_posts('r/python', max_results=50)
```

## 🔐 Configuration

### Environment Variables

```bash
# Twitter/X
export TWITTER_BEARER_TOKEN="your_bearer_token"
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"

# Add more platforms as needed
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
```

### In Code

```python
import os

adapter = get_adapter(
    'twitter',
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
)
```

## 🔄 Integration with Analytics Pipeline

### Current (Mock Data)

```python
# In app/workers/tasks.py
posts = generate_mock_posts(topic, count=120)
```

### With Real Twitter Data

```python
# In app/workers/tasks.py
import asyncio

# Fetch real posts
posts_data = asyncio.run(fetch_posts_from_adapter(topic, count=120, platform='twitter'))
```

### Multi-Platform Analysis

```python
async def fetch_from_multiple_platforms(topic: str):
    twitter_adapter = get_adapter('twitter')
    reddit_adapter = get_adapter('reddit')
    
    # Fetch from both platforms concurrently
    twitter_posts, reddit_posts = await asyncio.gather(
        twitter_adapter.fetch_posts(topic, max_results=100),
        reddit_adapter.fetch_posts(topic, max_results=100)
    )
    
    all_posts = twitter_posts + reddit_posts
    return [post.text for post in all_posts]
```

## 📝 API Reference

### SocialMediaAdapter (Base Class)

#### Methods

- **`fetch_posts(query, max_results, start_time, end_time)`**
  - Fetch posts from the platform
  - Returns: `List[SocialPost]`

- **`normalize_post(raw_post)`**
  - Convert platform-specific post to SocialPost
  - Returns: `SocialPost`

- **`validate_credentials()`**
  - Check if API credentials are valid
  - Returns: `bool`

- **`extract_hashtags(text)`**
  - Extract hashtags from text
  - Returns: `List[str]`

- **`extract_mentions(text)`**
  - Extract @mentions from text
  - Returns: `List[str]`

- **`extract_urls(text)`**
  - Extract URLs from text
  - Returns: `List[str]`

### TwitterAdapter

#### Additional Methods

- **`build_query(keywords, hashtags, mentions, exclude_retweets, language)`**
  - Build advanced Twitter search query
  - Returns: `str`

#### Example Queries

```python
# Simple hashtag search
posts = await adapter.fetch_posts('#AI')

# Advanced query
query = adapter.build_query(
    keywords=['climate', 'environment'],
    hashtags=['sustainability'],
    exclude_retweets=True,
    language='en'
)
posts = await adapter.fetch_posts(query)
```

## 🧪 Testing

### Mock Mode (Default)

The Twitter adapter includes mock data generation for testing:

```python
adapter = TwitterAdapter()
posts = await adapter.fetch_posts('#test', max_results=10)
# Returns mock posts for testing
```

### Real API Mode

To use real Twitter API:

1. Get Twitter API credentials from [developer.twitter.com](https://developer.twitter.com)
2. Set environment variables or pass credentials
3. Update `TwitterAdapter._fetch_mock_posts()` to use `_make_api_request()`

## 🎯 Best Practices

1. **Always use the factory**: `get_adapter()` instead of direct instantiation
2. **Handle rate limits**: Implement exponential backoff for API calls
3. **Cache credentials**: Don't pass credentials in every call
4. **Validate early**: Call `validate_credentials()` before fetching
5. **Use async**: All fetch operations should be async
6. **Normalize data**: Always convert to `SocialPost` format

## 🔮 Future Enhancements

- [ ] Add LinkedIn adapter
- [ ] Add Instagram adapter
- [ ] Add TikTok adapter
- [ ] Implement rate limiting
- [ ] Add retry logic with exponential backoff
- [ ] Support streaming APIs
- [ ] Add data validation with Pydantic
- [ ] Implement connection pooling
- [ ] Add metrics and monitoring

## 📚 Resources

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [Python AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)

## 🤝 Contributing

To add a new platform adapter:

1. Create `app/adapters/your_platform.py`
2. Implement `SocialMediaAdapter` interface
3. Register in `AdapterFactory`
4. Add tests
5. Update this README

---

**Built for the Async Social Analytics Platform** 🚀
