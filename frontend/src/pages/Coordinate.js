import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { GitBranch, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Coordinate = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [coordination, setCoordination] = useState({
    strategy: '',
    resources_needed: '',
    collaborators: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchRequestsNeedingCoordination();
  }, []);

  const fetchRequestsNeedingCoordination = async () => {
    try {
      const response = await axios.get(`${API}/requests`, {
        params: { status: 'in_progress' }
      });
      setRequests(response.data);
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  const handleSubmitCoordination = async () => {
    if (!selectedRequest || !coordination.strategy.trim()) {
      toast({
        title: "Error",
        description: "Please select a request and describe your coordination strategy",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post(`${API}/coordinate`, {
        request_id: selectedRequest.id,
        coordinator_id: localStorage.getItem('user_id') || `anon_${Date.now()}`,
        strategy: coordination.strategy,
        resources_needed: coordination.resources_needed.split(',').map(r => r.trim()).filter(Boolean),
        collaborators: coordination.collaborators.split(',').map(c => c.trim()).filter(Boolean)
      });

      toast({
        title: "Coordination Created",
        description: "Your coordination plan has been logged.",
      });

      setSelectedRequest(null);
      setCoordination({
        strategy: '',
        resources_needed: '',
        collaborators: ''
      });
    } catch (error) {
      console.error('Error submitting coordination:', error);
      toast({
        title: "Error",
        description: "Failed to submit coordination",
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
          <div className="p-3 bg-green-900/20 rounded-full">
            <GitBranch size={28} className="text-green-400" />
          </div>
          <div>
            <h1 className="text-4xl font-light">Coordinate</h1>
            <p className="text-gray-400 mt-1">Organize and strategize fulfillment</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-light mb-4">Requests in Progress</h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {requests.length > 0 ? (
                requests.map((request) => (
                  <Card
                    key={request.id}
                    className={`p-4 cursor-pointer transition-all ${
                      selectedRequest?.id === request.id
                        ? 'bg-green-900/30 border-green-500'
                        : 'bg-gray-900/50 border-gray-800 hover:border-green-500/50'
                    }`}
                    onClick={() => setSelectedRequest(request)}
                  >
                    <p className="text-sm text-gray-300 mb-2">{request.content}</p>
                    <Badge variant="outline" className="text-xs">{request.category}</Badge>
                  </Card>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">No requests in progress</p>
              )}
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-light mb-4">Coordination Plan</h2>
            {selectedRequest ? (
              <Card className="bg-gray-900/50 border-gray-800 p-6">
                <div className="space-y-6">
                  <div>
                    <Label htmlFor="strategy" className="text-gray-300 mb-2 block">
                      Strategy
                    </Label>
                    <Textarea
                      id="strategy"
                      placeholder="Describe how to fulfill this request..."
                      value={coordination.strategy}
                      onChange={(e) => setCoordination({ ...coordination, strategy: e.target.value })}
                      className="min-h-[150px] bg-black/50 border-gray-700 focus:border-green-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="resources" className="text-gray-300 mb-2 block">
                      Resources Needed (comma-separated)
                    </Label>
                    <Input
                      id="resources"
                      placeholder="e.g., volunteers, funding, tools"
                      value={coordination.resources_needed}
                      onChange={(e) => setCoordination({ ...coordination, resources_needed: e.target.value })}
                      className="bg-black/50 border-gray-700"
                    />
                  </div>

                  <div>
                    <Label htmlFor="collaborators" className="text-gray-300 mb-2 block">
                      Collaborators (comma-separated)
                    </Label>
                    <Input
                      id="collaborators"
                      placeholder="e.g., designer, developer, writer"
                      value={coordination.collaborators}
                      onChange={(e) => setCoordination({ ...coordination, collaborators: e.target.value })}
                      className="bg-black/50 border-gray-700"
                    />
                  </div>

                  <Button
                    onClick={handleSubmitCoordination}
                    disabled={isSubmitting}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    {isSubmitting ? 'Submitting...' : 'Create Coordination Plan'}
                  </Button>
                </div>
              </Card>
            ) : (
              <Card className="bg-gray-900/50 border-gray-800 p-12 text-center">
                <p className="text-gray-500">Select a request to coordinate</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Coordinate;
