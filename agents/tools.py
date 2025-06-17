"""Web search tool for fetching live trends and social signals."""
from typing import List, Dict, Any
from duckduckgo_search import DDGS
import json
import time
from datetime import datetime, timedelta


class WebSearchTool:
    """Tool for searching recent trends and news using DuckDuckGo."""
    
    def __init__(self, max_results: int = 10):
        """
        Initialize the web search tool.
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
        self.ddgs = DDGS()
    
    def search_trends(self, query: str, days_back: int = 90) -> List[Dict[str, Any]]:
        """
        Search for recent trends and news related to the query.
        
        Args:
            query: Search query string
            days_back: How many days back to search (default: 90)
            
        Returns:
            List of search results with title, snippet, and URL
        """
        try:
            # Calculate date range for recent results
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Enhance query with trend-related keywords
            enhanced_query = f"{query} trends social media viral hashtag 2025"
            
            results = []
            
            # Search news
            try:
                news_results = list(self.ddgs.news(
                    keywords=enhanced_query,
                    max_results=self.max_results // 2
                ))
                
                for result in news_results:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("url", ""),
                        "date": result.get("date", ""),
                        "source": "news"
                    })
            except Exception as e:
                print(f"News search failed: {e}")
            
            # Search general web
            try:
                web_results = list(self.ddgs.text(
                    keywords=enhanced_query,
                    max_results=self.max_results // 2
                ))
                
                for result in web_results:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("href", ""),
                        "date": "",
                        "source": "web"
                    })
            except Exception as e:
                print(f"Web search failed: {e}")
            
            return results[:self.max_results]
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_competitor_moves(self, brand_name: str, industry: str) -> List[Dict[str, Any]]:
        """
        Search for recent competitor activities and moves.
        
        Args:
            brand_name: Name of the brand/product
            industry: Industry category
            
        Returns:
            List of competitor-related search results
        """
        competitor_queries = [
            f"{industry} competitor news launch 2024",
            f"{brand_name} vs competitors recent",
            f"{industry} market trends new products"
        ]
        
        all_results = []
        for query in competitor_queries:
            results = self.search_trends(query, days_back=60)
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results[:self.max_results]
    
    def search_viral_content(self, topic: str) -> List[Dict[str, Any]]:
        """
        Search for viral content formats and hashtags related to topic.
        
        Args:
            topic: Topic to search viral content for
            
        Returns:
            List of viral content insights
        """
        viral_queries = [
            f"{topic} viral TikTok Instagram 2024",
            f"{topic} trending hashtags social media",
            f"{topic} viral marketing campaign recent"
        ]
        
        all_results = []
        for query in viral_queries:
            results = self.search_trends(query, days_back=30)  # More recent for viral content
            all_results.extend(results)
        
        return all_results[:self.max_results]
    
    def extract_trends_summary(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key trends from search results.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            List of trend summary strings
        """
        trends = []
        
        for result in search_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            # Extract key trend indicators
            if any(keyword in title.lower() or keyword in snippet.lower() 
                   for keyword in ["trending", "viral", "popular", "growing", "rising"]):
                
                # Create a concise trend summary
                trend_text = f"{title[:100]}..." if len(title) > 100 else title
                if snippet:
                    snippet_short = snippet[:150] + "..." if len(snippet) > 150 else snippet
                    trend_text += f" - {snippet_short}"
                
                trends.append(trend_text)
        
        return trends[:5]  # Return top 5 trends


# Global instance for easy import
web_search_tool = WebSearchTool()


def search_recent_trends(query: str, days_back: int = 90) -> List[str]:
    """
    Convenience function to search for recent trends.
    
    Args:
        query: Search query
        days_back: Days to look back
        
    Returns:
        List of trend summaries
    """
    results = web_search_tool.search_trends(query, days_back)
    return web_search_tool.extract_trends_summary(results) 