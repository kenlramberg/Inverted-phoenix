import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Search, Sparkles, Users, GitBranch, Zap, Lock } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Landing = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [userProgress, setUserProgress] = useState(null);
  const [userId] = useState(localStorage.getItem('user_id') || `anon_${Date.now()}`);
  const [sponsors, setSponsors] = useState([]);

  useEffect(() => {
    // Save user ID if new
    if (!localStorage.getItem('user_id')) {
      localStorage.setItem('user_id', userId);
    }
    fetchUserProgress();
    fetchSponsors();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchUserProgress = async () => {
    try {
      const response = await axios.get(`${API}/user/${userId}/progress`);
      setUserProgress(response.data);
    } catch (error) {
      console.error('Error fetching progress:', error);
      // Create user if doesn't exist
      try {
        await axios.post(`${API}/user`, { anonymous_id: userId });
        const response = await axios.get(`${API}/user/${userId}/progress`);
        setUserProgress(response.data);
      } catch (err) {
        console.error('Error creating user:', err);
      }
    }
  };

  const fetchSponsors = async () => {
    try {
      const response = await axios.get(`${API}/sponsors`, {
        params: { active_only: true, for_display: true }
      });
      setSponsors(response.data);
    } catch (error) {
      console.error('Error fetching sponsors:', error);
    }
  };

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
      borderColor: 'hover:border-purple-500/50',
      requiredLevel: 0,
      requiredActions: 0,
      instruction: 'Begin your journey'
    },
    {
      id: 'contribute',
      title: 'Contribute',
      description: 'Help fulfill requests through giving',
      icon: Users,
      path: '/contribute',
      color: 'from-blue-900/20 to-blue-600/20',
      borderColor: 'hover:border-blue-500/50',
      requiredLevel: 1,
      requiredActions: 1,
      instruction: 'Complete 1 action to unlock'
    },
    {
      id: 'coordinate',
      title: 'Coordinate',
      description: 'Organize and strategize fulfillment',
      icon: GitBranch,
      path: '/coordinate',
      color: 'from-green-900/20 to-green-600/20',
      borderColor: 'hover:border-green-500/50',
      requiredLevel: 2,
      requiredActions: 3,
      instruction: 'Complete 3 actions to unlock'
    },
    {
      id: 'execute',
      title: 'Execute',
      description: 'Take action and make wishes real',
      icon: Zap,
      path: '/execute',
      color: 'from-orange-900/20 to-orange-600/20',
      borderColor: 'hover:border-orange-500/50',
      requiredLevel: 3,
      requiredActions: 5,
      instruction: 'Complete 5 actions to unlock'
    }
  ];

  // Filter quadrants based on user progress - SEQUENTIAL REVELATION
  const getVisibleQuadrants = () => {
    if (!userProgress) return [quadrants[0]]; // Show only Ask initially
    
    const totalActions = userProgress.total_actions;
    
    // Show quadrants sequentially based on actions completed
    if (totalActions >= 5) return quadrants; // All unlocked
    if (totalActions >= 3) return quadrants.slice(0, 3); // Ask, Contribute, Coordinate
    if (totalActions >= 1) return quadrants.slice(0, 2); // Ask, Contribute
    return [quadrants[0]]; // Only Ask
  };

  const visibleQuadrants = getVisibleQuadrants();

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

        {/* The 4 Quadrants - Progressive Revelation */}
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light mb-4 text-gray-300">The Digital Wishing Well</h2>
          {userProgress && (
            <p className="text-sm text-gray-500 mb-8 text-center">
              Your actions: {userProgress.total_actions} • The next layer will reveal itself through participation
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {visibleQuadrants.map((quadrant) => {
              const Icon = quadrant.icon;
              const isUnlocked = userProgress ? userProgress.total_actions >= quadrant.requiredActions : quadrant.requiredActions === 0;
              
              return (
                <Card
                  key={quadrant.id}
                  className={`bg-gradient-to-br ${quadrant.color} border-gray-800 ${
                    isUnlocked ? quadrant.borderColor : 'border-gray-700'
                  } transition-all duration-300 ${
                    isUnlocked ? 'hover:scale-105 cursor-pointer' : 'cursor-not-allowed opacity-50'
                  } p-8 relative`}
                  onClick={() => isUnlocked && navigate(quadrant.path)}
                  data-testid={`quadrant-${quadrant.id}`}
                >
                  {!isUnlocked && (
                    <div className="absolute top-4 right-4">
                      <Lock size={20} className="text-gray-600" />
                    </div>
                  )}
                  <div className="flex flex-col items-center text-center">
                    <div className={`mb-4 p-4 ${isUnlocked ? 'bg-black/30' : 'bg-black/10'} rounded-full`}>
                      <Icon size={32} className={isUnlocked ? 'text-gray-300' : 'text-gray-600'} />
                    </div>
                    <h3 className="text-2xl font-light mb-2">{quadrant.title}</h3>
                    <p className={`text-sm ${isUnlocked ? 'text-gray-400' : 'text-gray-600'}`}>
                      {quadrant.description}
                    </p>
                    {!isUnlocked && (
                      <p className="text-xs text-gray-600 mt-3 italic">{quadrant.instruction}</p>
                    )}
                  </div>
                </Card>
              );
            })}
            
            {/* Show locked next quadrant as a hint */}
            {visibleQuadrants.length < quadrants.length && (
              <Card className="bg-gradient-to-br from-gray-900/10 to-gray-900/30 border-gray-800 border-dashed p-8 opacity-30">
                <div className="flex flex-col items-center text-center">
                  <div className="mb-4 p-4 bg-black/10 rounded-full">
                    <Lock size={32} className="text-gray-700" />
                  </div>
                  <h3 className="text-2xl font-light mb-2 text-gray-700">???</h3>
                  <p className="text-sm text-gray-700">
                    Continue participating to reveal the next layer
                  </p>
                </div>
              </Card>
            )}
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
      <footer className="border-t border-gray-900 bg-black py-12 mt-20">
        <div className="container mx-auto px-6">
          {/* Sponsor Logos */}
          {sponsors.length > 0 && (
            <div className="mb-12">
              <h3 className="text-center text-sm text-gray-600 mb-6 uppercase tracking-wide">
                Powered by Generosity
              </h3>
              <div className="flex flex-wrap justify-center items-center gap-8 max-w-4xl mx-auto">
                {sponsors.map((sponsor) => (
                  <a
                    key={sponsor.id}
                    href={sponsor.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="opacity-60 hover:opacity-100 transition-opacity"
                    title={sponsor.company_name}
                  >
                    <img
                      src={sponsor.logo_url}
                      alt={sponsor.company_name}
                      className="h-12 object-contain grayscale hover:grayscale-0 transition-all"
                    />
                  </a>
                ))}
              </div>
              <p className="text-center text-xs text-gray-700 mt-6">
                These companies donate products to AU4A members. No ads. Just generosity.
              </p>
            </div>
          )}
          
          <div className="text-center text-gray-600 text-sm">
            <p>AU4A - Ask Us 4 Anything</p>
            <p className="mt-2">Built on contribution, not extraction.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
