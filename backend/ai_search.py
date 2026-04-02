"""
AI-Powered Web Search Service for AU4A
No bias towards paid ads - filters and ranks based on quality and relevance only
"""
import os
import re
import asyncio
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()

class AIWebSearch:
    def __init__(self):
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using DuckDuckGo (no tracking, no ads) and process with AI
        """
        # Step 1: Get raw web results from DuckDuckGo
        raw_results = await self._duckduckgo_search(query, max_results * 2)
        
        if not raw_results:
            return []
        
        # Step 2: Filter out ads and sponsored content
        filtered_results = self._filter_ads(raw_results)
        
        # Step 3: Use AI to rank and summarize results (no commercial bias)
        ai_results = await self._ai_process_results(query, filtered_results, max_results)
        
        return ai_results
    
    async def _duckduckgo_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Search DuckDuckGo HTML (no tracking, no personalization)
        """
        try:
            # DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'us-en'  # English results
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, data=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result_div in soup.find_all('div', class_='result'):
                try:
                    title_elem = result_div.find('a', class_='result__a')
                    snippet_elem = result_div.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True)
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'duckduckgo'
                        })
                        
                        if len(results) >= max_results:
                            break
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def _filter_ads(self, results: List[Dict]) -> List[Dict]:
        """
        Filter out sponsored content and ads based on URL patterns and content
        """
        ad_patterns = [
            r'ad\.',
            r'ads\.',
            r'sponsored',
            r'partner',
            r'affiliate',
            r'doubleclick',
            r'googleadservices',
            r'amazon-adsystem',
            r'/ad/',
            r'/ads/',
        ]
        
        filtered = []
        for result in results:
            url = result['url'].lower()
            title = result['title'].lower()
            snippet = result['snippet'].lower()
            
            # Check if URL or content matches ad patterns
            is_ad = any(re.search(pattern, url) for pattern in ad_patterns)
            is_sponsored = 'sponsored' in title or 'sponsored' in snippet or 'ad' in title[:5]
            
            if not is_ad and not is_sponsored:
                filtered.append(result)
        
        return filtered
    
    async def _ai_process_results(self, query: str, results: List[Dict], max_results: int) -> List[Dict]:
        """
        Use AI to rank, summarize, and ensure no commercial bias
        """
        if not results:
            return []
        
        try:
            # Initialize LLM chat
            chat = LlmChat(
                api_key=self.emergent_key,
                session_id=f"search_{hash(query)}",
                system_message="""You are an unbiased search result processor for AU4A.

Your job:
1. Rank search results by RELEVANCE and QUALITY only
2. Filter out any commercial bias or promotional content
3. Create concise, helpful summaries
4. Assign a relevance score (0-10)
5. NEVER favor paid content, ads, or commercial interests

Return results in this exact JSON format:
[
  {
    "title": "original title",
    "url": "original url",
    "summary": "concise 1-2 sentence summary",
    "relevance_score": 8.5,
    "why_relevant": "brief explanation"
  }
]"""
            ).with_model("openai", "gpt-5.2")
            
            # Prepare results for AI
            results_text = "\n\n".join([
                f"Result {i+1}:\nTitle: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
                for i, r in enumerate(results[:10])
            ])
            
            prompt = f"""Query: "{query}"

Search Results:
{results_text}

Analyze these results and return the top {max_results} most relevant, unbiased results in JSON format.
Filter out any promotional or commercial-biased content.
Focus on informational value and accuracy."""
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse AI response
            import json
            # Extract JSON from response
            response_text = response.strip()
            
            # Try to find JSON in response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                ai_results = json.loads(json_match.group())
                
                # Add source field
                for result in ai_results:
                    result['result_source'] = 'web'
                    result['ai_processed'] = True
                
                return ai_results[:max_results]
            else:
                # Fallback: return original results with basic processing
                return self._fallback_ranking(results, max_results)
                
        except Exception as e:
            print(f"AI processing error: {e}")
            # Fallback to basic ranking
            return self._fallback_ranking(results, max_results)
    
    def _fallback_ranking(self, results: List[Dict], max_results: int) -> List[Dict]:
        """
        Fallback ranking when AI fails - simple relevance heuristics
        """
        processed = []
        for result in results[:max_results]:
            processed.append({
                'title': result['title'],
                'url': result['url'],
                'summary': result['snippet'],
                'relevance_score': 7.0,
                'why_relevant': 'Matched search query',
                'result_source': 'web',
                'ai_processed': False
            })
        return processed


async def hybrid_search(query: str, internal_results: List[Dict], max_total: int = 10) -> Dict:
    """
    Hybrid search: AU4A knowledge base + AI web search
    """
    result = {
        'query': query,
        'internal_count': len(internal_results),
        'external_count': 0,
        'results': []
    }
    
    # Add internal results first (prioritize AU4A knowledge)
    for item in internal_results:
        result['results'].append({
            **item,
            'result_source': 'au4a',
            'verified': True
        })
    
    # If we don't have enough internal results, search the web
    if len(internal_results) < 3:
        web_search = AIWebSearch()
        web_results = await web_search.search_web(query, max_results=max_total - len(internal_results))
        
        result['external_count'] = len(web_results)
        result['results'].extend(web_results)
    
    return result
