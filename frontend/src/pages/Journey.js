import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Lock, CheckCircle, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Journey = () => {
  const navigate = useNavigate();
  const [userProgress, setUserProgress] = useState(null);
  const [userId] = useState(localStorage.getItem('user_id') || `anon_${Date.now()}`);

  useEffect(() => {
    // Save user ID if new
    if (!localStorage.getItem('user_id')) {
      localStorage.setItem('user_id', userId);
    }
    
    const fetchData = async () => {
      await fetchUserProgress();
    };
    
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const fetchUserProgress = async () => {
    try {
      const response = await axios.get(`${API}/user/${userId}/progress`);
      setUserProgress(response.data);
    } catch (error) {
      console.error('Error fetching progress:', error);
      // Create user if doesn't exist
      try {
        await axios.post(`${API}/user`, { anonymous_id: userId });
        fetchUserProgress();
      } catch (err) {
        console.error('Error creating user:', err);
      }
    }
  };

  const layers = [
    {
      level: 0,
      title: "The Beginning",
      description: "You can Ask",
      feature: "ask",
      unlocked: true
    },
    {
      level: 1,
      title: "First Step",
      description: "Evaluate requests for ethics",
      feature: "evaluate",
      threshold: 5
    },
    {
      level: 2,
      title: "The Giver",
      description: "Contribute to fulfill wishes",
      feature: "contribute",
      threshold: 15
    },
    {
      level: 4,
      title: "The Strategist",
      description: "Coordinate complex fulfillment",
      feature: "coordinate",
      threshold: 30
    },
    {
      level: 6,
      title: "The Executor",
      description: "Take direct action",
      feature: "execute",
      threshold: 50
    },
    {
      level: 8,
      title: "The Searcher",
      description: "Advanced search capabilities",
      feature: "advanced_search",
      threshold: 100
    },
    {
      level: 10,
      title: "The Enlightened",
      description: "All features unlocked. You understand.",
      feature: "all",
      threshold: 500
    }
  ];

  if (!userProgress) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100 flex items-center justify-center">
        <p className="text-gray-500">Loading your journey...</p>
      </div>
    );
  }

  const progressPercent = (userProgress.total_actions / userProgress.next_level_threshold) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100">
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-100">
            <ArrowLeft size={20} />
          </Button>
          <div className="text-xl font-light tracking-wide">AU4A</div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-16 max-w-4xl">
        <div className="mb-12">
          <h1 className="text-4xl font-light mb-4">Your Journey</h1>
          <p className="text-gray-400">The system reveals itself gradually through participation.</p>
        </div>

        {/* Current Level */}
        <Card className="bg-gradient-to-br from-purple-900/20 to-purple-600/20 border-purple-500/50 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="text-sm text-purple-400 mb-1">Current Level</div>
              <div className="text-4xl font-light">{userProgress.participation_level}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400 mb-1">Total Actions</div>
              <div className="text-2xl font-light">{userProgress.total_actions}</div>
            </div>
          </div>
          
          <div className="mb-2">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>Progress to Next Level</span>
              <span>{userProgress.next_level_threshold} actions needed</span>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-12">
          <Card className="bg-gray-900/50 border-gray-800 p-4 text-center">
            <TrendingUp size={20} className="mx-auto mb-2 text-purple-400" />
            <div className="text-2xl font-light mb-1">{userProgress.total_actions}</div>
            <div className="text-xs text-gray-500">Total Actions</div>
          </Card>
        </div>

        {/* Layers */}
        <div className="space-y-4">
          <h2 className="text-2xl font-light mb-6">Layers of Revelation</h2>
          {layers.map((layer) => {
            const isUnlocked = userProgress.unlocked_features.includes(layer.feature) || layer.unlocked;
            const isCurrent = userProgress.participation_level === layer.level;
            
            return (
              <Card
                key={layer.level}
                className={`p-6 transition-all ${
                  isUnlocked
                    ? 'bg-gradient-to-r from-gray-900/50 to-purple-900/20 border-purple-500/30'
                    : 'bg-gray-900/30 border-gray-800'
                } ${isCurrent ? 'ring-2 ring-purple-500' : ''}`}
                data-testid="layer-card"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {isUnlocked ? (
                        <CheckCircle size={20} className="text-green-500" />
                      ) : (
                        <Lock size={20} className="text-gray-600" />
                      )}
                      <h3 className="text-xl font-light">{layer.title}</h3>
                      {isCurrent && (
                        <Badge className="bg-purple-600 text-white">Current</Badge>
                      )}
                    </div>
                    <p className={isUnlocked ? 'text-gray-400' : 'text-gray-600'}>
                      {layer.description}
                    </p>
                    {!isUnlocked && layer.threshold && (
                      <p className="text-xs text-gray-600 mt-2">
                        Unlocks at {layer.threshold} actions
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-light text-gray-500">L{layer.level}</div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Philosophy */}
        <div className="mt-16 p-8 border-t border-gray-900">
          <p className="text-gray-500 text-center italic">
            "Nothing is revealed all at once. This isn't that kind of project."
          </p>
        </div>
      </div>
    </div>
  );
};

export default Journey;
