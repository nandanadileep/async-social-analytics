"""
Example usage of the social media adapter system.

This script demonstrates how to use the adapter interface to fetch
and analyze social media data.
"""

import asyncio
from app.adapters.factory import get_adapter, AdapterFactory
from app.analytics.sentiment import analyze_sentiments
from app.analytics.words import extract_word_frequencies


async def example_basic_usage():
    """Basic example: Fetch posts from Twitter."""
    print("=" * 60)
    print("Example 1: Basic Twitter Adapter Usage")
    print("=" * 60)
    
    # Create Twitter adapter
    adapter = get_adapter('twitter')
    
    # Fetch posts
    topic = "AI"
    posts = await adapter.fetch_posts(topic, max_results=20)
    
    print(f"\nFetched {len(posts)} posts about '{topic}'")
    print("\nSample posts:")
    for i, post in enumerate(posts[:3], 1):
        print(f"\n{i}. @{post.author_username}:")
        print(f"   {post.text}")
        print(f"   ❤️ {post.likes} | 🔁 {post.retweets} | 💬 {post.replies}")


async def example_sentiment_analysis():
    """Example: Fetch posts and analyze sentiment."""
    print("\n" + "=" * 60)
    print("Example 2: Sentiment Analysis")
    print("=" * 60)
    
    adapter = get_adapter('twitter')
    
    topic = "Python"
    posts = await adapter.fetch_posts(topic, max_results=50)
    
    # Extract text
    texts = [post.text for post in posts]
    
    # Analyze sentiment
    sentiment = analyze_sentiments(texts)
    
    print(f"\nSentiment Analysis for '{topic}':")
    print(f"  Positive: {sentiment['positive']} ({sentiment['positive']/len(posts)*100:.1f}%)")
    print(f"  Neutral:  {sentiment['neutral']} ({sentiment['neutral']/len(posts)*100:.1f}%)")
    print(f"  Negative: {sentiment['negative']} ({sentiment['negative']/len(posts)*100:.1f}%)")


async def example_word_frequency():
    """Example: Extract top keywords."""
    print("\n" + "=" * 60)
    print("Example 3: Keyword Extraction")
    print("=" * 60)
    
    adapter = get_adapter('twitter')
    
    topic = "blockchain"
    posts = await adapter.fetch_posts(topic, max_results=100)
    
    # Extract text
    texts = [post.text for post in posts]
    
    # Get word frequencies
    word_freq = extract_word_frequencies(texts, top_n=10)
    
    print(f"\nTop 10 keywords for '{topic}':")
    for i, (word, count) in enumerate(word_freq, 1):
        print(f"  {i:2d}. {word:15s} - {count:3d} occurrences")


async def example_advanced_query():
    """Example: Use advanced query building."""
    print("\n" + "=" * 60)
    print("Example 4: Advanced Query Building")
    print("=" * 60)
    
    from app.adapters.twitter import TwitterAdapter
    
    adapter = TwitterAdapter()
    
    # Build complex query
    query = adapter.build_query(
        keywords=["AI", "machine learning"],
        hashtags=["tech"],
        exclude_retweets=True,
        language="en"
    )
    
    print(f"\nBuilt query: {query}")
    
    posts = await adapter.fetch_posts(query, max_results=30)
    print(f"Fetched {len(posts)} posts")
    
    # Show hashtag distribution
    all_hashtags = []
    for post in posts:
        all_hashtags.extend(post.hashtags)
    
    from collections import Counter
    hashtag_counts = Counter(all_hashtags).most_common(5)
    
    print("\nTop hashtags:")
    for tag, count in hashtag_counts:
        print(f"  #{tag}: {count}")


async def example_multi_topic():
    """Example: Compare multiple topics."""
    print("\n" + "=" * 60)
    print("Example 5: Multi-Topic Comparison")
    print("=" * 60)
    
    adapter = get_adapter('twitter')
    
    topics = ["Python", "JavaScript", "Rust"]
    
    print("\nComparing sentiment across topics:\n")
    print(f"{'Topic':<15} {'Positive':<10} {'Neutral':<10} {'Negative':<10}")
    print("-" * 50)
    
    for topic in topics:
        posts = await adapter.fetch_posts(topic, max_results=50)
        texts = [post.text for post in posts]
        sentiment = analyze_sentiments(texts)
        
        pos_pct = sentiment['positive'] / len(posts) * 100
        neu_pct = sentiment['neutral'] / len(posts) * 100
        neg_pct = sentiment['negative'] / len(posts) * 100
        
        print(f"{topic:<15} {pos_pct:>6.1f}%    {neu_pct:>6.1f}%    {neg_pct:>6.1f}%")


async def example_post_details():
    """Example: Access detailed post information."""
    print("\n" + "=" * 60)
    print("Example 6: Detailed Post Information")
    print("=" * 60)
    
    adapter = get_adapter('twitter')
    
    posts = await adapter.fetch_posts("#opensource", max_results=5)
    
    print("\nDetailed post information:\n")
    
    for i, post in enumerate(posts, 1):
        print(f"Post {i}:")
        print(f"  ID: {post.id}")
        print(f"  Author: @{post.author_username} (ID: {post.author_id})")
        print(f"  Created: {post.created_at}")
        print(f"  Text: {post.text[:100]}...")
        print(f"  Engagement:")
        print(f"    - Likes: {post.likes}")
        print(f"    - Retweets: {post.retweets}")
        print(f"    - Replies: {post.replies}")
        print(f"  Hashtags: {', '.join(post.hashtags) if post.hashtags else 'None'}")
        print(f"  Mentions: {', '.join(post.mentions) if post.mentions else 'None'}")
        print(f"  Language: {post.language}")
        print()


async def main():
    """Run all examples."""
    print("\n🚀 Social Media Adapter Examples\n")
    
    # Show supported platforms
    platforms = AdapterFactory.get_supported_platforms()
    print(f"Supported platforms: {', '.join(platforms)}\n")
    
    # Run examples
    await example_basic_usage()
    await example_sentiment_analysis()
    await example_word_frequency()
    await example_advanced_query()
    await example_multi_topic()
    await example_post_details()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print("\nNote: These examples use mock data.")
    print("To use real Twitter data, configure your API credentials.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
