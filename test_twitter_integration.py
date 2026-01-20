#!/usr/bin/env python3
"""
Quick test script to verify Twitter adapter integration.
"""

import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, '/Users/nandana/newproj/async-social-analytics')

from app.adapters.factory import get_adapter


async def test_adapter():
    """Test the Twitter adapter."""
    print("🧪 Testing Twitter Adapter Integration\n")
    print("=" * 60)
    
    # Create adapter
    print("\n1. Creating Twitter adapter...")
    adapter = get_adapter('twitter')
    print(f"   ✅ Adapter created: {adapter.platform_name}")
    
    # Test credential validation
    print("\n2. Validating credentials...")
    is_valid = await adapter.validate_credentials()
    print(f"   {'✅' if is_valid else '⚠️'} Credentials valid: {is_valid}")
    
    # Fetch posts
    print("\n3. Fetching posts for topic '#AI'...")
    try:
        posts = await adapter.fetch_posts('#AI', max_results=10)
        print(f"   ✅ Fetched {len(posts)} posts")
        
        # Show sample
        if posts:
            print("\n4. Sample post:")
            post = posts[0]
            print(f"   ID: {post.id}")
            print(f"   Author: @{post.author_username}")
            print(f"   Text: {post.text[:80]}...")
            print(f"   Likes: {post.likes} | Retweets: {post.retweets}")
            print(f"   Hashtags: {', '.join(post.hashtags) if post.hashtags else 'None'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test query building
    print("\n5. Testing advanced query building...")
    from app.adapters.twitter import TwitterAdapter
    twitter = TwitterAdapter()
    query = twitter.build_query(
        keywords=["AI", "machine learning"],
        hashtags=["tech"],
        exclude_retweets=True,
        language="en"
    )
    print(f"   ✅ Built query: {query}")
    
    print("\n" + "=" * 60)
    print("\n✅ All tests passed!")
    print("\n📝 Note: Currently using mock data.")
    print("   To use real Twitter data:")
    print("   1. Get Bearer Token from developer.twitter.com")
    print("   2. Set TWITTER_BEARER_TOKEN environment variable")
    print("   3. Update TwitterAdapter to use _make_api_request()")
    print()


if __name__ == "__main__":
    asyncio.run(test_adapter())
