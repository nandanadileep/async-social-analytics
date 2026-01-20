"""
Adapter factory for creating social media adapters.

This module provides a centralized way to create and manage different
social media adapters.
"""

from typing import Dict, Type, Optional
from app.adapters.base import SocialMediaAdapter
from app.adapters.twitter import TwitterAdapter


class AdapterFactory:
    """
    Factory for creating social media adapters.
    
    Supports registering new adapters and creating instances based on
    platform name.
    """
    
    _adapters: Dict[str, Type[SocialMediaAdapter]] = {
        "twitter": TwitterAdapter,
        "x": TwitterAdapter,  # Alias for Twitter
    }
    
    @classmethod
    def register_adapter(
        cls,
        platform_name: str,
        adapter_class: Type[SocialMediaAdapter]
    ):
        """
        Register a new adapter for a platform.
        
        Args:
            platform_name: Name of the platform (e.g., 'reddit', 'linkedin')
            adapter_class: Adapter class implementing SocialMediaAdapter
        """
        cls._adapters[platform_name.lower()] = adapter_class
    
    @classmethod
    def create_adapter(
        cls,
        platform: str,
        **credentials
    ) -> SocialMediaAdapter:
        """
        Create an adapter instance for the specified platform.
        
        Args:
            platform: Platform name ('twitter', 'reddit', etc.)
            **credentials: Platform-specific credentials
            
        Returns:
            Initialized adapter instance
            
        Raises:
            ValueError: If platform is not supported
            
        Example:
            adapter = AdapterFactory.create_adapter(
                'twitter',
                bearer_token='your_token'
            )
        """
        platform = platform.lower()
        
        if platform not in cls._adapters:
            raise ValueError(
                f"Unsupported platform: {platform}. "
                f"Supported platforms: {', '.join(cls._adapters.keys())}"
            )
        
        adapter_class = cls._adapters[platform]
        return adapter_class(**credentials)
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """
        Get list of supported platforms.
        
        Returns:
            List of platform names
        """
        return list(cls._adapters.keys())


# Convenience function
def get_adapter(platform: str = "twitter", **credentials) -> SocialMediaAdapter:
    """
    Get an adapter instance for the specified platform.
    
    Args:
        platform: Platform name (default: 'twitter')
        **credentials: Platform-specific credentials
        
    Returns:
        Initialized adapter instance
    """
    return AdapterFactory.create_adapter(platform, **credentials)
