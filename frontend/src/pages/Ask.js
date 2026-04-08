import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Ask = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    content: '',
    category: 'general'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.content.trim()) {
      toast({
        title: "Error",
        description: "Please describe your request",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await axios.post(`${API}/ask`, {
        content: formData.content,
        category: formData.category,
        submitted_by: localStorage.getItem('user_id') || 'anonymous'
      });

      toast({
        title: "Request Submitted",
        description: "Your request is now being evaluated by the community.",
      });

      // Prompt user to contribute
      setTimeout(() => {
        const shouldContribute = window.confirm(
          "You've asked for something. Would you like to tell us what YOU can give in return?"
        );
        
        if (shouldContribute) {
          navigate('/give');
        } else {
          navigate(`/request/${response.data.id}`);
        }
      }, 1500);
    } catch (error) {
      console.error('Error submitting request:', error);
      toast({
        title: "Error",
        description: "Failed to submit request. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100">
      <Toaster />
      
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-100">
            <ArrowLeft size={20} />
          </Button>
          <div className="text-xl font-light tracking-wide">AU4A</div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-16 max-w-3xl">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-3 bg-purple-900/20 rounded-full">
            <Sparkles size={28} className="text-purple-400" />
          </div>
          <div>
            <h1 className="text-4xl font-light">Ask</h1>
            <p className="text-gray-400 mt-1">Submit your wish, question, or need</p>
          </div>
        </div>

        <Card className="bg-gray-900/50 border-gray-800 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="content" className="text-gray-300 mb-2 block">
                What do you need?
              </Label>
              <Textarea
                id="content"
                placeholder="Describe your request in detail. Be clear, specific, and ethical."
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="min-h-[200px] bg-black/50 border-gray-700 focus:border-purple-500 text-gray-100"
                data-testid="request-content-input"
              />
              <p className="text-xs text-gray-500 mt-2">
                All requests are evaluated for legality, morality, and potential harm.
              </p>
            </div>

            <div>
              <Label htmlFor="category" className="text-gray-300 mb-2 block">
                Category
              </Label>
              <Input
                id="category"
                type="text"
                placeholder="e.g., knowledge, material, connection, skill"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="bg-black/50 border-gray-700 focus:border-purple-500 text-gray-100"
                data-testid="request-category-input"
              />
            </div>

            <div className="pt-4">
              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                data-testid="submit-request-button"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Request'}
              </Button>
            </div>
          </form>
        </Card>

        {/* Guidelines */}
        <div className="mt-12 space-y-4 text-sm text-gray-500">
          <h3 className="text-gray-300 font-normal">Guidelines</h3>
          <ul className="space-y-2 list-disc list-inside">
            <li>Requests must be ethical, legal, and genuinely meaningful</li>
            <li>The community will evaluate your request for potential harm</li>
            <li>Approved requests will be visible to contributors</li>
            <li>This is built on goodwill, not extraction</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Ask;
