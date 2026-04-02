import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Search as SearchIcon, ArrowLeft, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Search = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchStats, setSearchStats] = useState({ internal: 0, external: 0 });

  // Get query from URL params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q) {
      setSearchQuery(q);
      performSearch(q);
    }
  }, []);

  const performSearch = async (query) => {
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const response = await axios.get(`${API}/search`, {
        params: { q: query }
      });
      
      // Handle new hybrid search response format
      const data = response.data;
      if (data.results) {
        setResults(data.results);
        setSearchStats({
          internal: data.internal_count || 0,
          external: data.external_count || 0
        });
      } else {
        // Fallback for old format
        setResults(response.data);
        setSearchStats({ internal: response.data.length, external: 0 });
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
      setSearchStats({ internal: 0, external: 0 });
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    performSearch(searchQuery);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-100">
            <ArrowLeft size={20} />
          </Button>
          <div className="text-xl font-light tracking-wide">AU4A</div>
        </div>
      </header>

      {/* Search Section */}
      <div className="container mx-auto px-6 py-16 max-w-4xl">
        <div className="mb-12">
          <h1 className="text-4xl font-light mb-6">Search</h1>
          <form onSubmit={handleSearch}>
            <div className="relative">
              <SearchIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
              <Input
                type="text"
                placeholder="Search the knowledge base..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 pr-4 py-6 text-lg bg-gray-900/50 border-gray-700 focus:border-purple-500"
                data-testid="search-input"
              />
            </div>
          </form>
          <p className="text-sm text-gray-500 mt-4">
            Hybrid AI search: AU4A knowledge base + unbiased web search (no paid ads)
          </p>
          {(searchStats.internal > 0 || searchStats.external > 0) && (
            <div className="flex gap-4 mt-2 text-xs text-gray-600">
              <span>AU4A Results: {searchStats.internal}</span>
              <span>Web Results: {searchStats.external}</span>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="space-y-4">
          {isSearching ? (
            <div className="text-center text-gray-500 py-12">Searching...</div>
          ) : results.length > 0 ? (
            results.map((result, index) => {
              const isAU4A = result.result_source === 'au4a';
              const isWeb = result.result_source === 'web';
              
              return (
                <Card 
                  key={result.id || index} 
                  className={`p-6 transition-colors ${
                    isAU4A 
                      ? 'bg-gradient-to-r from-purple-900/20 to-gray-900/50 border-purple-500/30' 
                      : 'bg-gray-900/50 border-gray-800 hover:border-blue-500/50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex gap-2 items-center flex-wrap">
                      {isAU4A && (
                        <>
                          <Badge className="bg-purple-600 text-white">AU4A Knowledge</Badge>
                          {result.verified && (
                            <Badge className="bg-green-900/30 text-green-400">Verified</Badge>
                          )}
                        </>
                      )}
                      {isWeb && (
                        <>
                          <Badge variant="outline" className="border-blue-500 text-blue-400">Web Search</Badge>
                          {result.ai_processed && (
                            <Badge variant="outline" className="text-xs">AI Processed</Badge>
                          )}
                        </>
                      )}
                      {result.category && (
                        <Badge variant="outline" className="text-xs">{result.category}</Badge>
                      )}
                    </div>
                    {result.relevance_score && (
                      <span className="text-xs text-gray-600">
                        Relevance: {result.relevance_score.toFixed(1)}/10
                      </span>
                    )}
                    {result.quality_score && !result.relevance_score && (
                      <span className="text-xs text-gray-600">
                        Quality: {result.quality_score.toFixed(1)}/10
                      </span>
                    )}
                  </div>
                  
                  <h3 className="text-xl font-normal mb-2 text-gray-200">
                    {result.title}
                  </h3>
                  
                  <p className="text-gray-400 mb-3">
                    {result.summary || result.content?.substring(0, 200) || result.snippet}
                    {(result.content?.length > 200 || result.snippet) && '...'}
                  </p>
                  
                  {result.why_relevant && (
                    <p className="text-sm text-gray-500 italic mb-3">
                      Why relevant: {result.why_relevant}
                    </p>
                  )}
                  
                  {result.url && (
                    <a 
                      href={result.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    >
                      {result.url}
                      <ExternalLink size={12} />
                    </a>
                  )}
                  
                  {result.fulfilled_request_id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/request/${result.fulfilled_request_id}`)}
                      className="mt-2"
                      data-testid="view-result-button"
                    >
                      View Request Details
                    </Button>
                  )}
                </Card>
              );
            })
          ) : searchQuery && !isSearching ? (
            <div className="text-center text-gray-500 py-12">
              <p>No results found for "{searchQuery}"</p>
              <p className="text-sm mt-2">
                {searchStats.internal === 0 && 'The knowledge base is still growing. Web search returned no unbiased results.'}
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default Search;
