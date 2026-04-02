import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Scale, ArrowLeft, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Evaluate = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [pendingRequests, setPendingRequests] = useState([]);
  const [currentRequest, setCurrentRequest] = useState(null);
  const [evaluation, setEvaluation] = useState({
    legality_score: 5,
    morality_score: 5,
    harm_score: 5,
    cultural_impact_score: 5,
    comments: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchPendingRequests();
  }, []);

  const fetchPendingRequests = async () => {
    try {
      const response = await axios.get(`${API}/evaluate/pending`);
      setPendingRequests(response.data);
      if (response.data.length > 0 && !currentRequest) {
        setCurrentRequest(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching pending requests:', error);
    }
  };

  const handleSubmitEvaluation = async () => {
    if (!currentRequest) return;

    setIsSubmitting(true);
    try {
      await axios.post(`${API}/evaluate`, {
        request_id: currentRequest.id,
        evaluator_id: localStorage.getItem('user_id') || `anon_${Date.now()}`,
        ...evaluation
      });

      toast({
        title: "Evaluation Submitted",
        description: "Thank you for helping maintain ethical standards.",
      });

      // Move to next request
      const remainingRequests = pendingRequests.filter(r => r.id !== currentRequest.id);
      setPendingRequests(remainingRequests);
      setCurrentRequest(remainingRequests[0] || null);
      
      // Reset evaluation
      setEvaluation({
        legality_score: 5,
        morality_score: 5,
        harm_score: 5,
        cultural_impact_score: 5,
        comments: ''
      });
    } catch (error) {
      console.error('Error submitting evaluation:', error);
      toast({
        title: "Error",
        description: "Failed to submit evaluation",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
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

      <div className="container mx-auto px-6 py-16 max-w-4xl">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-3 bg-purple-900/20 rounded-full">
            <Scale size={28} className="text-purple-400" />
          </div>
          <div>
            <h1 className="text-4xl font-light">Evaluate</h1>
            <p className="text-gray-400 mt-1">Help maintain ethical standards</p>
          </div>
        </div>

        {currentRequest ? (
          <Card className="bg-gray-900/50 border-gray-800 p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-light mb-4">Request to Evaluate</h2>
              <div className="bg-black/30 p-6 rounded-lg mb-6">
                <p className="text-gray-300 leading-relaxed">{currentRequest.content}</p>
                <div className="mt-4 text-sm text-gray-500">
                  Category: {currentRequest.category}
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <Label className="text-gray-300 mb-3 block">
                  Legality (1 = Illegal, 10 = Legal)
                </Label>
                <Slider
                  value={[evaluation.legality_score]}
                  onValueChange={([value]) => setEvaluation({ ...evaluation, legality_score: value })}
                  min={1}
                  max={10}
                  step={1}
                  className="mb-2"
                />
                <div className="text-sm text-gray-500">Score: {evaluation.legality_score}</div>
              </div>

              <div>
                <Label className="text-gray-300 mb-3 block">
                  Morality (1 = Unethical, 10 = Highly Ethical)
                </Label>
                <Slider
                  value={[evaluation.morality_score]}
                  onValueChange={([value]) => setEvaluation({ ...evaluation, morality_score: value })}
                  min={1}
                  max={10}
                  step={1}
                  className="mb-2"
                />
                <div className="text-sm text-gray-500">Score: {evaluation.morality_score}</div>
              </div>

              <div>
                <Label className="text-gray-300 mb-3 block">
                  Potential Harm (1 = No Harm, 10 = High Harm)
                </Label>
                <Slider
                  value={[evaluation.harm_score]}
                  onValueChange={([value]) => setEvaluation({ ...evaluation, harm_score: value })}
                  min={1}
                  max={10}
                  step={1}
                  className="mb-2"
                />
                <div className="text-sm text-gray-500">Score: {evaluation.harm_score}</div>
              </div>

              <div>
                <Label className="text-gray-300 mb-3 block">
                  Cultural Impact (1 = Negative, 10 = Positive)
                </Label>
                <Slider
                  value={[evaluation.cultural_impact_score]}
                  onValueChange={([value]) => setEvaluation({ ...evaluation, cultural_impact_score: value })}
                  min={1}
                  max={10}
                  step={1}
                  className="mb-2"
                />
                <div className="text-sm text-gray-500">Score: {evaluation.cultural_impact_score}</div>
              </div>

              <div>
                <Label htmlFor="comments" className="text-gray-300 mb-2 block">
                  Comments (Optional)
                </Label>
                <Textarea
                  id="comments"
                  placeholder="Explain your evaluation..."
                  value={evaluation.comments}
                  onChange={(e) => setEvaluation({ ...evaluation, comments: e.target.value })}
                  className="bg-black/50 border-gray-700 focus:border-purple-500"
                />
              </div>

              <Button
                onClick={handleSubmitEvaluation}
                disabled={isSubmitting}
                className="w-full bg-purple-600 hover:bg-purple-700"
                data-testid="submit-evaluation-button"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Evaluation'}
              </Button>
            </div>
          </Card>
        ) : (
          <Card className="bg-gray-900/50 border-gray-800 p-12 text-center">
            <CheckCircle size={48} className="mx-auto mb-4 text-green-500" />
            <h2 className="text-2xl font-light mb-2">All Caught Up!</h2>
            <p className="text-gray-400">No pending requests to evaluate at the moment.</p>
            <Button onClick={() => navigate('/')} className="mt-6">
              Return Home
            </Button>
          </Card>
        )}

        <div className="mt-8 text-sm text-gray-500">
          <p>Pending evaluations: {pendingRequests.length}</p>
        </div>
      </div>
    </div>
  );
};

export default Evaluate;
