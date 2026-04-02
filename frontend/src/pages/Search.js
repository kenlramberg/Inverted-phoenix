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
      setResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
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
            This is a human-curated knowledge base. No external APIs. No paid ranking. Pure information.
          </p>
        </div>

        {/* Results */}
        <div className="space-y-4">
          {isSearching ? (
            <div className="text-center text-gray-500 py-12">Searching...</div>
          ) : results.length > 0 ? (
            results.map((result) => (
              <Card key={result.id} className="bg-gray-900/50 border-gray-800 p-6 hover:border-purple-500/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-normal mb-2">{result.title}</h3>
                    <p className="text-gray-400 mb-3">{result.content.substring(0, 200)}...</p>
                    <div className="flex gap-2 items-center">
                      <Badge variant="outline" className="text-xs">{result.category}</Badge>
                      {result.verified && (
                        <Badge className="text-xs bg-green-900/30 text-green-400">Verified</Badge>
                      )}
                      <span className="text-xs text-gray-600">Quality: {result.quality_score.toFixed(1)}/10</span>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/request/${result.fulfilled_request_id}`)}
                    data-testid="view-result-button"
                  >
                    <ExternalLink size={16} />
                  </Button>
                </div>
              </Card>
            ))
          ) : searchQuery && !isSearching ? (
            <div className="text-center text-gray-500 py-12">
              <p>No results found for "{searchQuery}"</p>
              <p className="text-sm mt-2">The knowledge base grows as requests are fulfilled.</p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default Search;
