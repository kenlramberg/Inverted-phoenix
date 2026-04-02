import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Users, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Contribute = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [approvedRequests, setApprovedRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [contribution, setContribution] = useState({
    contribution_type: 'bestow',
    content: '',
    details: '',
    trade_offer: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchApprovedRequests();
  }, []);

  const fetchApprovedRequests = async () => {
    try {
      const response = await axios.get(`${API}/requests`, {
        params: { status: 'approved' }
      });
      setApprovedRequests(response.data);
    } catch (error) {
      console.error('Error fetching approved requests:', error);
    }
  };

  const handleSubmitContribution = async () => {
    if (!selectedRequest || !contribution.content.trim()) {
      toast({
        title: "Error",
        description: "Please select a request and describe your contribution",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post(`${API}/contribute`, {
        request_id: selectedRequest.id,
        contributor_id: localStorage.getItem('user_id') || `anon_${Date.now()}`,
        ...contribution
      });

      toast({
        title: "Contribution Submitted",
        description: "Thank you for giving!",
      });

      setSelectedRequest(null);
      setContribution({
        contribution_type: 'bestow',
        content: '',
        details: '',
        trade_offer: ''
      });
    } catch (error) {
      console.error('Error submitting contribution:', error);
      toast({
        title: "Error",
        description: "Failed to submit contribution",
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
          <div className="p-3 bg-blue-900/20 rounded-full">
            <Users size={28} className="text-blue-400" />
          </div>
          <div>
            <h1 className="text-4xl font-light">Contribute</h1>
            <p className="text-gray-400 mt-1">Help fulfill requests through giving</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Approved Requests List */}
          <div>
            <h2 className="text-2xl font-light mb-4">Approved Requests</h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {approvedRequests.length > 0 ? (
                approvedRequests.map((request) => (
                  <Card
                    key={request.id}
                    className={`p-4 cursor-pointer transition-all ${
                      selectedRequest?.id === request.id
                        ? 'bg-blue-900/30 border-blue-500'
                        : 'bg-gray-900/50 border-gray-800 hover:border-blue-500/50'
                    }`}
                    onClick={() => setSelectedRequest(request)}
                    data-testid="request-card"
                  >
                    <p className="text-sm text-gray-300 mb-2">{request.content}</p>
                    <div className="flex gap-2 items-center">
                      <Badge variant="outline" className="text-xs">{request.category}</Badge>
                      {request.ethical_score && (
                        <span className="text-xs text-gray-500">
                          Ethics: {request.ethical_score.toFixed(1)}/10
                        </span>
                      )}
                    </div>
                  </Card>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">No approved requests yet</p>
              )}
            </div>
          </div>

          {/* Contribution Form */}
          <div>
            <h2 className="text-2xl font-light mb-4">Your Contribution</h2>
            {selectedRequest ? (
              <Card className="bg-gray-900/50 border-gray-800 p-6">
                <div className="space-y-6">
                  <div>
                    <Label className="text-gray-300 mb-2 block">Contribution Type</Label>
                    <Select
                      value={contribution.contribution_type}
                      onValueChange={(value) => setContribution({ ...contribution, contribution_type: value })}
                    >
                      <SelectTrigger className="bg-black/50 border-gray-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="borrow">Borrow</SelectItem>
                        <SelectItem value="barter">Barter</SelectItem>
                        <SelectItem value="buy">Buy</SelectItem>
                        <SelectItem value="bring">Bring</SelectItem>
                        <SelectItem value="bestow">Bestow (Give)</SelectItem>
                        <SelectItem value="befriend">Befriend</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="content" className="text-gray-300 mb-2 block">
                      How can you help?
                    </Label>
                    <Textarea
                      id="content"
                      placeholder="Describe what you can contribute..."
                      value={contribution.content}
                      onChange={(e) => setContribution({ ...contribution, content: e.target.value })}
                      className="bg-black/50 border-gray-700 focus:border-blue-500"
                      data-testid="contribution-content-input"
                    />
                  </div>

                  <div>
                    <Label htmlFor="details" className="text-gray-300 mb-2 block">
                      Details
                    </Label>
                    <Input
                      id="details"
                      placeholder="Additional details..."
                      value={contribution.details}
                      onChange={(e) => setContribution({ ...contribution, details: e.target.value })}
                      className="bg-black/50 border-gray-700"
                    />
                  </div>

                  {contribution.contribution_type === 'barter' && (
                    <div>
                      <Label htmlFor="trade" className="text-gray-300 mb-2 block">
                        What would you like in exchange?
                      </Label>
                      <Input
                        id="trade"
                        placeholder="Your trade offer..."
                        value={contribution.trade_offer}
                        onChange={(e) => setContribution({ ...contribution, trade_offer: e.target.value })}
                        className="bg-black/50 border-gray-700"
                      />
                    </div>
                  )}

                  <Button
                    onClick={handleSubmitContribution}
                    disabled={isSubmitting}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    data-testid="submit-contribution-button"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Contribution'}
                  </Button>
                </div>
              </Card>
            ) : (
              <Card className="bg-gray-900/50 border-gray-800 p-12 text-center">
                <p className="text-gray-500">Select a request to contribute</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contribute;
