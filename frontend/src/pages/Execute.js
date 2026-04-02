import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Zap, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Execute = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [execution, setExecution] = useState({
    action_taken: '',
    verification_proof: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchRequestsReadyForExecution();
  }, []);

  const fetchRequestsReadyForExecution = async () => {
    try {
      const response = await axios.get(`${API}/requests`, {
        params: { status: 'in_progress' }
      });
      setRequests(response.data);
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  const handleSubmitExecution = async () => {
    if (!selectedRequest || !execution.action_taken.trim()) {
      toast({
        title: "Error",
        description: "Please describe the action you've taken",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post(`${API}/execute`, {
        request_id: selectedRequest.id,
        executor_id: localStorage.getItem('user_id') || `anon_${Date.now()}`,
        action_taken: execution.action_taken,
        verification_proof: execution.verification_proof
      });

      toast({
        title: "Execution Logged",
        description: "Your action has been recorded.",
      });

      setSelectedRequest(null);
      setExecution({
        action_taken: '',
        verification_proof: ''
      });
    } catch (error) {
      console.error('Error submitting execution:', error);
      toast({
        title: "Error",
        description: "Failed to log execution",
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

      <div className="container mx-auto px-6 py-16 max-w-6xl">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-3 bg-orange-900/20 rounded-full">
            <Zap size={28} className="text-orange-400" />
          </div>
          <div>
            <h1 className="text-4xl font-light">Execute</h1>
            <p className="text-gray-400 mt-1">Take action and make wishes real</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-light mb-4">Ready for Execution</h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {requests.length > 0 ? (
                requests.map((request) => (
                  <Card
                    key={request.id}
                    className={`p-4 cursor-pointer transition-all ${
                      selectedRequest?.id === request.id
                        ? 'bg-orange-900/30 border-orange-500'
                        : 'bg-gray-900/50 border-gray-800 hover:border-orange-500/50'
                    }`}
                    onClick={() => setSelectedRequest(request)}
                  >
                    <p className="text-sm text-gray-300 mb-2">{request.content}</p>
                    <Badge variant="outline" className="text-xs">{request.category}</Badge>
                  </Card>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">No requests ready for execution</p>
              )}
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-light mb-4">Log Your Action</h2>
            {selectedRequest ? (
              <Card className="bg-gray-900/50 border-gray-800 p-6">
                <div className="space-y-6">
                  <div>
                    <Label htmlFor="action" className="text-gray-300 mb-2 block">
                      Action Taken
                    </Label>
                    <Textarea
                      id="action"
                      placeholder="Describe what you did to fulfill this request..."
                      value={execution.action_taken}
                      onChange={(e) => setExecution({ ...execution, action_taken: e.target.value })}
                      className="min-h-[150px] bg-black/50 border-gray-700 focus:border-orange-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="proof" className="text-gray-300 mb-2 block">
                      Verification Proof (Optional)
                    </Label>
                    <Textarea
                      id="proof"
                      placeholder="Link to proof, tracking number, photo URL, etc."
                      value={execution.verification_proof}
                      onChange={(e) => setExecution({ ...execution, verification_proof: e.target.value })}
                      className="bg-black/50 border-gray-700"
                    />
                  </div>

                  <Button
                    onClick={handleSubmitExecution}
                    disabled={isSubmitting}
                    className="w-full bg-orange-600 hover:bg-orange-700"
                  >
                    {isSubmitting ? 'Submitting...' : 'Log Execution'}
                  </Button>
                </div>
              </Card>
            ) : (
              <Card className="bg-gray-900/50 border-gray-800 p-12 text-center">
                <p className="text-gray-500">Select a request to execute</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Execute;
