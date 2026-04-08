import React, { useState } from 'react';
import axios from 'axios';
import { Heart, Sparkles, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GivingPoll = () => {
  const [step, setStep] = useState(1);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    offer_type: '',
    description: '',
    category: 'general',
    availability: '',
    location: '',
    contact_info: ''
  });

  const handleSubmit = async () => {
    try {
      await axios.post(`${API}/offer`, {
        ...formData,
        source: 'external_poll',
        contributor_id: 'anonymous',
        tags: formData.description.toLowerCase().split(' ').filter(w => w.length > 3).slice(0, 5)
      });
      
      setIsSubmitted(true);
    } catch (error) {
      console.error('Error submitting offer:', error);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <Card className="max-w-md w-full bg-gray-900/50 border-gray-800 p-12 text-center">
          <Check size={64} className="mx-auto mb-6 text-green-500" />
          <h2 className="text-3xl font-light mb-4 text-gray-100">Thank You</h2>
          <p className="text-gray-400">
            Your contribution has been recorded. 
          </p>
          <p className="text-gray-500 text-sm mt-4">
            Someone, somewhere, will benefit from your generosity.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100 p-6">
      <div className="max-w-2xl mx-auto py-16">
        {/* Header - Minimal, No Branding */}
        <div className="text-center mb-12">
          <Heart size={48} className="mx-auto mb-6 text-purple-400" />
          <h1 className="text-4xl font-light mb-4">What could you give?</h1>
          <p className="text-gray-400">
            A simple question. An honest answer. That's all.
          </p>
        </div>

        <Card className="bg-gray-900/50 border-gray-800 p-8">
          {/* Step 1: Type of Offering */}
          {step === 1 && (
            <div className="space-y-6 fade-in">
              <div>
                <Label className="text-gray-300 mb-3 block text-lg">
                  What kind of thing could you share?
                </Label>
                <Select
                  value={formData.offer_type}
                  onValueChange={(value) => setFormData({ ...formData, offer_type: value })}
                >
                  <SelectTrigger className="bg-black/50 border-gray-700 text-lg py-6">
                    <SelectValue placeholder="Choose one..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="skill">A skill I could teach</SelectItem>
                    <SelectItem value="item">Something I own</SelectItem>
                    <SelectItem value="knowledge">Knowledge or information</SelectItem>
                    <SelectItem value="time">My time or effort</SelectItem>
                    <SelectItem value="connection">A helpful connection</SelectItem>
                    <SelectItem value="other">Something else</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={() => setStep(2)}
                disabled={!formData.offer_type}
                className="w-full bg-purple-600 hover:bg-purple-700 py-6 text-lg"
              >
                Continue
              </Button>
            </div>
          )}

          {/* Step 2: Description */}
          {step === 2 && (
            <div className="space-y-6 fade-in">
              <div>
                <Label className="text-gray-300 mb-3 block text-lg">
                  Tell us more
                </Label>
                <Textarea
                  placeholder="What specifically could you offer? Be as detailed or vague as you like."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="min-h-[150px] bg-black/50 border-gray-700 text-lg"
                />
                <p className="text-xs text-gray-600 mt-2">
                  This is anonymous. No judgment. Just honest contribution.
                </p>
              </div>

              <div className="flex gap-4">
                <Button
                  variant="ghost"
                  onClick={() => setStep(1)}
                  className="flex-1"
                >
                  Back
                </Button>
                <Button
                  onClick={() => setStep(3)}
                  disabled={!formData.description.trim()}
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                >
                  Continue
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Optional Details */}
          {step === 3 && (
            <div className="space-y-6 fade-in">
              <div>
                <Label className="text-gray-300 mb-2 block">
                  When could you help? (Optional)
                </Label>
                <Input
                  placeholder="e.g., weekends, evenings, anytime..."
                  value={formData.availability}
                  onChange={(e) => setFormData({ ...formData, availability: e.target.value })}
                  className="bg-black/50 border-gray-700"
                />
              </div>

              <div>
                <Label className="text-gray-300 mb-2 block">
                  Location, if relevant (Optional)
                </Label>
                <Input
                  placeholder="e.g., city, online, worldwide..."
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="bg-black/50 border-gray-700"
                />
              </div>

              <div>
                <Label className="text-gray-300 mb-2 block">
                  How can we reach you? (Optional)
                </Label>
                <Input
                  type="email"
                  placeholder="email@example.com"
                  value={formData.contact_info}
                  onChange={(e) => setFormData({ ...formData, contact_info: e.target.value })}
                  className="bg-black/50 border-gray-700"
                />
                <p className="text-xs text-gray-600 mt-2">
                  Only if someone needs exactly what you offered. Never shared.
                </p>
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
                  onClick={handleSubmit}
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                >
                  Submit
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Footer - Minimal */}
        <div className="text-center mt-12">
          <p className="text-gray-600 text-sm">
            Built on generosity, not extraction.
          </p>
        </div>
      </div>
    </div>
  );
};

export default GivingPoll;
