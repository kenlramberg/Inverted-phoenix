import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles, Users, GitBranch, Zap } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const Landing = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const quadrants = [
    {
      id: 'ask',
      title: 'Ask',
      description: 'Submit your wish, question, or need',
      icon: Sparkles,
      path: '/ask',
      color: 'from-purple-900/20 to-purple-600/20',
      borderColor: 'hover:border-purple-500/50'
    },
    {
      id: 'contribute',
      title: 'Contribute',
      description: 'Help fulfill requests through giving',
      icon: Users,
      path: '/contribute',
      color: 'from-blue-900/20 to-blue-600/20',
      borderColor: 'hover:border-blue-500/50'
    },
    {
      id: 'coordinate',
      title: 'Coordinate',
      description: 'Organize and strategize fulfillment',
      icon: GitBranch,
      path: '/coordinate',
      color: 'from-green-900/20 to-green-600/20',
      borderColor: 'hover:border-green-500/50'
    },
    {
      id: 'execute',
      title: 'Execute',
      description: 'Take action and make wishes real',
      icon: Zap,
      path: '/execute',
      color: 'from-orange-900/20 to-orange-600/20',
      borderColor: 'hover:border-orange-500/50'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="text-xl font-light tracking-wide">AU4A</div>
          <nav className="flex gap-6 text-sm">
            <button onClick={() => navigate('/evaluate')} className="hover:text-purple-400 transition-colors">
              Evaluate
            </button>
            <button onClick={() => navigate('/journey')} className="hover:text-purple-400 transition-colors">
              Journey
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 pt-24 pb-16 text-center fade-in">
        <h1 className="text-6xl md:text-7xl font-extralight mb-6 tracking-tight">
          Do you want the answers <span className="text-purple-400">2</span> everything…?
        </h1>
        <p className="text-xl md:text-2xl text-gray-400 font-light mb-4">
          The Greatest Social Experiment in History
        </p>
        <p className="text-gray-500 max-w-2xl mx-auto mb-12">
          A digital wishing well. A search engine of truth. A place where human goodwill becomes reality.
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-20">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
            <Input
              type="text"
              placeholder="Search the knowledge base..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 pr-4 py-6 text-lg bg-gray-900/50 border-gray-700 focus:border-purple-500 rounded-full"
              data-testid="search-input"
            />
          </div>
        </form>

        {/* The 4 Quadrants */}
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light mb-8 text-gray-300">The Digital Wishing Well</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {quadrants.map((quadrant) => {
              const Icon = quadrant.icon;
              return (
                <Card
                  key={quadrant.id}
                  className={`bg-gradient-to-br ${quadrant.color} border-gray-800 ${quadrant.borderColor} transition-all duration-300 hover:scale-105 cursor-pointer p-8`}
                  onClick={() => navigate(quadrant.path)}
                  data-testid={`quadrant-${quadrant.id}`}
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="mb-4 p-4 bg-black/30 rounded-full">
                      <Icon size={32} className="text-gray-300" />
                    </div>
                    <h3 className="text-2xl font-light mb-2">{quadrant.title}</h3>
                    <p className="text-gray-400 text-sm">{quadrant.description}</p>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Philosophy Section */}
      <section className="container mx-auto px-6 py-20 border-t border-gray-900">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-light mb-6">What is this?</h2>
          <div className="space-y-4 text-gray-400 leading-relaxed">
            <p>
              Something is being built here. Not a company. Not a product. Not a platform in the usual sense.
            </p>
            <p>
              It doesn't sell. It doesn't rank by money. It doesn't belong to anyone.
            </p>
            <p className="text-purple-400 font-normal">
              It belongs to <em>us</em>.
            </p>
            <p className="pt-6 text-sm text-gray-500">
              Knowledge is freedom. When used with positive intention, knowledge improves humanity.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-900 bg-black py-8 mt-20">
        <div className="container mx-auto px-6 text-center text-gray-600 text-sm">
          <p>AU4A - Ask Us 4 Anything</p>
          <p className="mt-2">Built on contribution, not extraction.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
