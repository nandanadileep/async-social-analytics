# Adapter System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Analytics Application                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Adapter Factory                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Platform Registry:                                       │   │
│  │  • twitter  → TwitterAdapter                              │   │
│  │  • reddit   → RedditAdapter                               │   │
│  │  • linkedin → LinkedInAdapter                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              SocialMediaAdapter (Abstract Base)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Abstract Methods:                                        │   │
│  │  • fetch_posts()                                          │   │
│  │  • normalize_post()                                       │   │
│  │  • validate_credentials()                                 │   │
│  │                                                            │   │
│  │  Helper Methods:                                          │   │
│  │  • extract_hashtags()                                     │   │
│  │  • extract_mentions()                                     │   │
│  │  • extract_urls()                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────┬───────────────────┬───────────────────┬───────────┘
              │                   │                   │
              ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ TwitterAdapter  │ │ RedditAdapter   │ │ LinkedInAdapter │
    │                 │ │                 │ │                 │
    │ • Twitter API   │ │ • Reddit API    │ │ • LinkedIn API  │
    │ • Query builder │ │ • Subreddit     │ │ • Company pages │
    │ • Rate limiting │ │   search        │ │ • Job posts     │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────────────────────────────────────────────┐
    │                  Platform APIs                           │
    │  • Twitter API v2                                        │
    │  • Reddit API                                            │
    │  • LinkedIn API                                          │
    └─────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Standardized SocialPost                     │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │  • id: str                                         │  │
    │  │  • text: str                                       │  │
    │  │  • author_id: str                                  │  │
    │  │  • author_username: str                            │  │
    │  │  • created_at: datetime                            │  │
    │  │  • likes: int                                      │  │
    │  │  • retweets: int                                   │  │
    │  │  • replies: int                                    │  │
    │  │  • hashtags: List[str]                             │  │
    │  │  • mentions: List[str]                             │  │
    │  │  • urls: List[str]                                 │  │
    │  │  • raw_data: Dict                                  │  │
    │  └───────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Analytics Pipeline                          │
    │  • Sentiment Analysis                                    │
    │  • Keyword Extraction                                    │
    │  • Trend Detection                                       │
    │  • Batch Processing                                      │
    └─────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User Request
   └─> Topic: "#AI"
       
2. Adapter Factory
   └─> Creates TwitterAdapter instance
       
3. TwitterAdapter
   └─> fetch_posts("#AI", max_results=100)
       │
       ├─> Build query: "#AI -is:retweet lang:en"
       │
       ├─> Call Twitter API
       │   └─> GET /2/tweets/search/recent
       │
       └─> Normalize responses
           └─> Convert to SocialPost[]
       
4. Analytics Processing
   ├─> Extract text from posts
   ├─> Sentiment analysis
   ├─> Word frequency extraction
   └─> Generate insights
       
5. Cache & Return
   └─> Store in Redis
   └─> Return to user
```

## Integration Points

### Current System Integration

```python
# Before (Mock Data)
posts = generate_mock_posts(topic, count=120)

# After (Real Data via Adapter)
from app.adapters.factory import get_adapter

adapter = get_adapter('twitter')
social_posts = await adapter.fetch_posts(topic, max_results=120)
posts = [post.text for post in social_posts]
```

### Multi-Platform Support

```python
async def fetch_from_all_platforms(topic: str):
    adapters = {
        'twitter': get_adapter('twitter'),
        'reddit': get_adapter('reddit'),
        'linkedin': get_adapter('linkedin')
    }
    
    results = {}
    for platform, adapter in adapters.items():
        posts = await adapter.fetch_posts(topic, max_results=100)
        results[platform] = posts
    
    return results
```

## Extension Pattern

### Adding a New Platform

```
1. Create adapter class
   └─> app/adapters/new_platform.py
       └─> class NewPlatformAdapter(SocialMediaAdapter)
           ├─> fetch_posts()
           ├─> normalize_post()
           └─> validate_credentials()

2. Register adapter
   └─> AdapterFactory.register_adapter('new_platform', NewPlatformAdapter)

3. Use immediately
   └─> adapter = get_adapter('new_platform')
       └─> posts = await adapter.fetch_posts(query)
```

## Benefits

✅ **Pluggable**: Add new platforms without changing core code
✅ **Testable**: Mock adapters for testing
✅ **Consistent**: All platforms return same data structure
✅ **Scalable**: Easy to add rate limiting, caching, retries
✅ **Type-safe**: Standardized SocialPost dataclass
✅ **Async-first**: Built for high-performance concurrent fetching
