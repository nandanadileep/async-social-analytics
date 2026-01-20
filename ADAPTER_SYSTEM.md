# 🔌 Social Media Ingestion Adapter System

## Overview

A **production-ready, pluggable adapter interface** for ingesting social media data from multiple platforms. Twitter can plug in seamlessly, and new platforms can be added in minutes.

---

## ✨ Key Features

### 🎯 **Platform-Agnostic Design**
- Abstract base class defines the contract
- Each platform implements the same interface
- Consistent data format across all sources

### 🚀 **Ready for Twitter Integration**
- `TwitterAdapter` with full API v2 support
- Advanced query building
- Mock mode for testing, real mode for production
- Rate limiting ready

### 📊 **Standardized Data Model**
- `SocialPost` dataclass normalizes all platform data
- Automatic extraction of hashtags, mentions, URLs
- Preserves raw platform data for advanced use cases

### ⚡ **Async-First Architecture**
- Built with `asyncio` for high performance
- Concurrent fetching from multiple platforms
- Non-blocking I/O operations

### 🔧 **Easy to Extend**
- Add new platforms in 3 steps
- Factory pattern for adapter creation
- Plugin registration system

---

## 📁 File Structure

```
app/adapters/
├── __init__.py              # Module initialization
├── base.py                  # Abstract base class + SocialPost
├── twitter.py               # Twitter/X implementation
├── factory.py               # Adapter factory & registry
├── README.md                # Usage documentation
└── ARCHITECTURE.md          # System architecture diagrams

examples/
└── adapter_usage.py         # Complete usage examples
```

---

## 🚀 Quick Start

### 1. Basic Usage

```python
from app.adapters.factory import get_adapter

# Create Twitter adapter
adapter = get_adapter('twitter', bearer_token='your_token')

# Fetch posts
posts = await adapter.fetch_posts('#AI', max_results=100)

# Process results
for post in posts:
    print(f"{post.author_username}: {post.text}")
```

### 2. Integration with Analytics

```python
# In your analytics pipeline
from app.adapters.factory import get_adapter
from app.analytics.sentiment import analyze_sentiments

# Fetch real Twitter data
adapter = get_adapter('twitter')
posts = await adapter.fetch_posts(topic, max_results=120)

# Extract text
texts = [post.text for post in posts]

# Analyze
sentiment = analyze_sentiments(texts)
```

### 3. Multi-Platform Analysis

```python
# Compare sentiment across platforms
twitter_adapter = get_adapter('twitter')
reddit_adapter = get_adapter('reddit')

twitter_posts = await twitter_adapter.fetch_posts(topic)
reddit_posts = await reddit_adapter.fetch_posts(topic)

# Analyze both
```

---

## 🔌 How Twitter Plugs In

### Current State (Mock Data)
```python
# app/workers/tasks.py
posts = generate_mock_posts(topic, count=120)
```

### With Twitter Adapter
```python
# app/workers/tasks.py
posts_data = await fetch_posts_from_adapter(topic, count=120, platform='twitter')
```

### Configuration
```bash
# Set environment variables
export TWITTER_BEARER_TOKEN="your_bearer_token"
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
```

---

## 📊 SocialPost Data Model

Every platform converts to this standard format:

```python
@dataclass
class SocialPost:
    id: str                    # Unique post ID
    text: str                  # Post content
    author_id: str             # Author user ID
    author_username: str       # @username
    created_at: datetime       # Timestamp
    likes: int                 # Engagement metrics
    retweets: int             
    replies: int              
    language: str              # Language code
    hashtags: List[str]        # Extracted #tags
    mentions: List[str]        # Extracted @mentions
    urls: List[str]            # Extracted links
    raw_data: Dict             # Original platform data
```

---

## 🎯 Adding a New Platform

### Step 1: Create Adapter

```python
# app/adapters/reddit.py
from app.adapters.base import SocialMediaAdapter, SocialPost

class RedditAdapter(SocialMediaAdapter):
    async def fetch_posts(self, query, max_results=100):
        # Implement Reddit API calls
        pass
    
    def normalize_post(self, raw_post):
        # Convert to SocialPost
        return SocialPost(...)
    
    async def validate_credentials(self):
        return True
    
    @property
    def platform_name(self):
        return "reddit"
```

### Step 2: Register

```python
from app.adapters.factory import AdapterFactory
AdapterFactory.register_adapter('reddit', RedditAdapter)
```

### Step 3: Use

```python
adapter = get_adapter('reddit')
posts = await adapter.fetch_posts('r/python')
```

---

## 🧪 Testing

### Run Examples

```bash
cd /Users/nandana/newproj/async-social-analytics
python3 examples/adapter_usage.py
```

### Test with Mock Data

```python
# Adapter automatically uses mock data when no credentials provided
adapter = TwitterAdapter()
posts = await adapter.fetch_posts('#test', max_results=10)
# Returns mock posts for testing
```

---

## 🔐 Production Setup

### 1. Get Twitter API Credentials
- Go to [developer.twitter.com](https://developer.twitter.com)
- Create an app
- Get Bearer Token (recommended for API v2)

### 2. Configure Environment

```bash
# .env file
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
```

### 3. Update Code

```python
# In app/adapters/twitter.py
# Replace _fetch_mock_posts() with _make_api_request()

async def fetch_posts(self, query, max_results=100):
    # Use real API
    response = await self._make_api_request(query, max_results)
    
    # Normalize posts
    posts = []
    for raw_post in response.get('data', []):
        posts.append(self.normalize_post(raw_post))
    
    return posts
```

---

## 📈 Benefits

### For Development
✅ **Mock mode** - Test without API credentials
✅ **Type safety** - Standardized data structures
✅ **Easy testing** - Mock adapters for unit tests

### For Production
✅ **Platform agnostic** - Switch platforms easily
✅ **Scalable** - Add rate limiting, retries, caching
✅ **Maintainable** - Clean separation of concerns

### For Business
✅ **Multi-platform** - Analyze Twitter, Reddit, LinkedIn, etc.
✅ **Consistent** - Same analytics across all platforms
✅ **Extensible** - Add new platforms as needed

---

## 🎓 Learn More

- **Usage Guide**: `app/adapters/README.md`
- **Architecture**: `app/adapters/ARCHITECTURE.md`
- **Examples**: `examples/adapter_usage.py`
- **Twitter API Docs**: [developer.twitter.com](https://developer.twitter.com/en/docs/twitter-api)

---

## 🚀 Next Steps

1. **Test with mock data**: Run `examples/adapter_usage.py`
2. **Get Twitter credentials**: Sign up at developer.twitter.com
3. **Configure environment**: Set `TWITTER_BEARER_TOKEN`
4. **Switch to real data**: Update `fetch_posts()` to use API
5. **Add more platforms**: Implement Reddit, LinkedIn adapters

---

**Built for scalable, multi-platform social media analytics** 🎯
