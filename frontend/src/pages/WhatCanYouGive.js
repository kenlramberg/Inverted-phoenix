import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Gift, ArrowLeft, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WhatCanYouGive = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [offers, setOffers] = useState([]);
  const [currentOffer, setCurrentOffer] = useState({
    offer_type: '',
    description: '',
    category: 'general',
    availability: ''
  });

  const offerTypes = [
    { value: 'skill', label: 'A skill you could teach', icon: '🎓', prompt: 'What skill could you teach someone?' },
    { value: 'item', label: 'Something you could lend or give', icon: '📦', prompt: 'What do you have that someone might need?' },
    { value: 'knowledge', label: 'Knowledge or advice', icon: '💡', prompt: 'What do you know that could help others?' },
    { value: 'time', label: 'Your time or effort', icon: '⏰', prompt: 'How could you spend time helping someone?' },
    { value: 'connection', label: 'A helpful introduction', icon: '🤝', prompt: 'Who do you know that could help someone?' }
  ];

  const handleAddOffer = () => {
    if (currentOffer.description.trim()) {
      setOffers([...offers, currentOffer]);
      setCurrentOffer({
        offer_type: '',
        description: '',
        category: 'general',
        availability: ''
      });
      setStep(1);
    }
  };

  const handleSubmitAll = async () => {
    try {
      for (const offer of offers) {
        await axios.post(`${API}/offer`, {
          ...offer,
          contributor_id: localStorage.getItem('user_id') || 'anonymous',
          source: 'internal_app',
          tags: offer.description.toLowerCase().split(' ').filter(w => w.length > 3).slice(0, 5)
        });
      }

      toast({
        title: "Thank you for giving",
        description: `${offers.length} contribution${offers.length > 1 ? 's' : ''} added to the system.`,
      });

      setTimeout(() => navigate('/journey'), 2000);
    } catch (error) {
      console.error('Error submitting offers:', error);
      toast({
        title: "Error",
        description: "Failed to submit contributions",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100">
      <Toaster />
      
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-100">
            <ArrowLeft size={20} />
          </Button>
          <div className="text-xl font-light tracking-wide">AU4A</div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-16 max-w-3xl">
        {/* Introduction */}
        {step === 1 && offers.length === 0 && (
          <div className="text-center mb-12 fade-in">
            <Gift size={64} className="mx-auto mb-6 text-purple-400" />
            <h1 className="text-5xl font-light mb-6">You've asked...</h1>
            <h2 className="text-3xl font-light mb-6 text-gray-400">Now, what can YOU give?</h2>
            <p className="text-gray-500 max-w-xl mx-auto mb-8">
              The system works when everyone contributes. What could you offer to help someone else?
            </p>
            <Button
              onClick={() => setStep(2)}
              className="bg-purple-600 hover:bg-purple-700 px-8 py-6 text-lg"
            >
              I'm ready to contribute
            </Button>
          </div>
        )}

        {/* Choose Type */}
        {step === 2 && (
          <Card className="bg-gray-900/50 border-gray-800 p-8 fade-in">
            <h2 className="text-2xl font-light mb-6">What kind of contribution?</h2>
            <div className="grid grid-cols-1 gap-4">
              {offerTypes.map((type) => (
                <Card
                  key={type.value}
                  className="p-6 cursor-pointer hover:bg-purple-900/20 transition-all border-gray-800 hover:border-purple-500/50"
                  onClick={() => {
                    setCurrentOffer({ ...currentOffer, offer_type: type.value });
                    setStep(3);
                  }}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-3xl">{type.icon}</span>
                    <span className="text-lg text-gray-300">{type.label}</span>
                  </div>
                </Card>
              ))}
            </div>
            {offers.length > 0 && (
              <Button
                variant="ghost"
                onClick={() => setStep(4)}
                className="w-full mt-6"
              >
                Skip - I'm done adding
              </Button>
            )}
          </Card>
        )}

        {/* Describe Offering */}
        {step === 3 && (
          <Card className="bg-gray-900/50 border-gray-800 p-8 fade-in">
            <h2 className="text-2xl font-light mb-2">
              {offerTypes.find(t => t.value === currentOffer.offer_type)?.prompt}
            </h2>
            <p className="text-gray-500 mb-6">Be specific. Be honest.</p>

            <div className="space-y-6">
              <div>
                <Label htmlFor="description" className="text-gray-300 mb-2 block">
                  Description
                </Label>
                <Textarea
                  id="description"
                  placeholder="Describe what you can offer..."
                  value={currentOffer.description}
                  onChange={(e) => setCurrentOffer({ ...currentOffer, description: e.target.value })}
                  className="min-h-[150px] bg-black/50 border-gray-700"
                />
              </div>

              <div>
                <Label htmlFor="availability" className="text-gray-300 mb-2 block">
                  When/How (Optional)
                </Label>
                <Input
                  id="availability"
                  placeholder="e.g., weekends, online, in-person..."
                  value={currentOffer.availability}
                  onChange={(e) => setCurrentOffer({ ...currentOffer, availability: e.target.value })}
                  className="bg-black/50 border-gray-700"
                />
              </div>

              <div className="flex gap-4">
                <Button
                  variant="ghost"
                  onClick={() => setStep(2)}
                  className="flex-1"
                >
                  Back
                </Button>
                <Button
                  onClick={handleAddOffer}
                  disabled={!currentOffer.description.trim()}
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                >
                  Add This Contribution
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Review & Submit */}
        {step === 4 && (
          <div className="fade-in">
            <div className="flex items-center gap-3 mb-8">
              <Sparkles size={28} className="text-purple-400" />
              <h2 className="text-3xl font-light">Your Contributions</h2>
            </div>

            <div className="space-y-4 mb-8">
              {offers.map((offer, index) => (
                <Card key={index} className="bg-gray-900/50 border-gray-800 p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-sm text-purple-400 mb-2">
                        {offerTypes.find(t => t.value === offer.offer_type)?.label}
                      </div>
                      <p className="text-gray-300">{offer.description}</p>
                      {offer.availability && (
                        <p className="text-sm text-gray-500 mt-2">{offer.availability}</p>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setOffers(offers.filter((_, i) => i !== index))}
                      className="text-gray-600 hover:text-red-400"
                    >
                      Remove
                    </Button>
                  </div>
                </Card>
              ))}
            </div>

            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={() => setStep(2)}
                className="flex-1"
              >
                Add Another
              </Button>
              <Button
                onClick={handleSubmitAll}
                className="flex-1 bg-purple-600 hover:bg-purple-700"
              >
                Submit All ({offers.length})
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WhatCanYouGive;
