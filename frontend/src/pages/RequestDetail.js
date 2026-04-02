import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RequestDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [contributions, setContributions] = useState([]);
  const [coordinations, setCoordinations] = useState([]);
  const [executions, setExecutions] = useState([]);

  useEffect(() => {
    if (id) {
      fetchRequestDetails();
    }
  }, [id]);

  const fetchRequestDetails = async () => {
    try {
      const [reqRes, evalRes, contribRes, coordRes, execRes] = await Promise.all([
        axios.get(`${API}/request/${id}`),
        axios.get(`${API}/evaluate/${id}`),
        axios.get(`${API}/contributions/${id}`),
        axios.get(`${API}/coordinate/${id}`),
        axios.get(`${API}/execute/${id}`)
      ]);

      setRequest(reqRes.data);
      setEvaluations(evalRes.data);
      setContributions(contribRes.data);
      setCoordinations(coordRes.data);
      setExecutions(execRes.data);
    } catch (error) {
      console.error('Error fetching request details:', error);
    }
  };

  if (!request) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-gray-100 flex items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  const statusColors = {
    pending: 'bg-yellow-900/30 text-yellow-400',
    evaluating: 'bg-blue-900/30 text-blue-400',
    approved: 'bg-green-900/30 text-green-400',
    rejected: 'bg-red-900/30 text-red-400',
    in_progress: 'bg-purple-900/30 text-purple-400',
    fulfilled: 'bg-emerald-900/30 text-emerald-400'
  };

  const statusIcons = {
    pending: Clock,
    evaluating: AlertCircle,
    approved: CheckCircle,
    rejected: AlertCircle,
    in_progress: Clock,
    fulfilled: CheckCircle
  };

  const StatusIcon = statusIcons[request.status] || Clock;

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

      <div className="container mx-auto px-6 py-16 max-w-5xl">
        {/* Request Header */}
        <Card className="bg-gray-900/50 border-gray-800 p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <StatusIcon size={24} className={statusColors[request.status].split(' ')[1]} />
                <Badge className={statusColors[request.status]}>
                  {request.status.replace('_', ' ')}
                </Badge>
                <Badge variant="outline">{request.category}</Badge>
              </div>
              <p className="text-xl text-gray-300 leading-relaxed">{request.content}</p>
            </div>
          </div>

          {/* Ethics Scores */}
          {request.ethical_score && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-800">
              <div>
                <div className="text-xs text-gray-500 mb-1">Ethical Score</div>
                <div className="text-2xl font-light">{request.ethical_score.toFixed(1)}/10</div>
              </div>
              {request.legality_score && (
                <div>
                  <div className="text-xs text-gray-500 mb-1">Legality</div>
                  <div className="text-2xl font-light">{request.legality_score.toFixed(1)}/10</div>
                </div>
              )}
              {request.harm_score && (
                <div>
                  <div className="text-xs text-gray-500 mb-1">Harm Level</div>
                  <div className="text-2xl font-light">{request.harm_score.toFixed(1)}/10</div>
                </div>
              )}
              <div>
                <div className="text-xs text-gray-500 mb-1">Evaluations</div>
                <div className="text-2xl font-light">{request.evaluation_count}/{request.required_evaluations}</div>
              </div>
            </div>
          )}
        </Card>

        {/* Tabs for different stages */}
        <Tabs defaultValue="evaluations" className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900/50">
            <TabsTrigger value="evaluations">Evaluations ({evaluations.length})</TabsTrigger>
            <TabsTrigger value="contributions">Contributions ({contributions.length})</TabsTrigger>
            <TabsTrigger value="coordination">Coordination ({coordinations.length})</TabsTrigger>
            <TabsTrigger value="execution">Execution ({executions.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="evaluations" className="mt-6 space-y-4">
            {evaluations.length > 0 ? (
              evaluations.map((evaluation) => (
                <Card key={evaluation.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <div className="grid grid-cols-4 gap-4 mb-3">
                    <div>
                      <div className="text-xs text-gray-500">Legality</div>
                      <div className="text-lg">{evaluation.legality_score}/10</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Morality</div>
                      <div className="text-lg">{evaluation.morality_score}/10</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Harm</div>
                      <div className="text-lg">{evaluation.harm_score}/10</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Cultural</div>
                      <div className="text-lg">{evaluation.cultural_impact_score}/10</div>
                    </div>
                  </div>
                  {evaluation.comments && (
                    <p className="text-sm text-gray-400 mt-3 pt-3 border-t border-gray-800">{evaluation.comments}</p>
                  )}
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No evaluations yet</p>
            )}
          </TabsContent>

          <TabsContent value="contributions" className="mt-6 space-y-4">
            {contributions.length > 0 ? (
              contributions.map((contrib) => (
                <Card key={contrib.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <div className="flex items-start justify-between mb-3">
                    <Badge>{contrib.contribution_type}</Badge>
                    <Badge className={contrib.verified ? 'bg-green-900/30 text-green-400' : 'bg-gray-700'}>
                      {contrib.verified ? 'Verified' : 'Pending'}
                    </Badge>
                  </div>
                  <p className="text-gray-300">{contrib.content}</p>
                  {contrib.details && <p className="text-sm text-gray-500 mt-2">{contrib.details}</p>}
                  {contrib.trade_offer && (
                    <p className="text-sm text-purple-400 mt-2">Trade offer: {contrib.trade_offer}</p>
                  )}
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No contributions yet</p>
            )}
          </TabsContent>

          <TabsContent value="coordination" className="mt-6 space-y-4">
            {coordinations.length > 0 ? (
              coordinations.map((coord) => (
                <Card key={coord.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <Badge className="mb-3">{coord.status}</Badge>
                  <p className="text-gray-300 mb-4">{coord.strategy}</p>
                  {coord.resources_needed.length > 0 && (
                    <div className="mb-2">
                      <div className="text-xs text-gray-500 mb-1">Resources Needed:</div>
                      <div className="flex flex-wrap gap-2">
                        {coord.resources_needed.map((resource, i) => (
                          <Badge key={i} variant="outline" className="text-xs">{resource}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No coordination plans yet</p>
            )}
          </TabsContent>

          <TabsContent value="execution" className="mt-6 space-y-4">
            {executions.length > 0 ? (
              executions.map((exec) => (
                <Card key={exec.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <Badge className="mb-3">{exec.status}</Badge>
                  <p className="text-gray-300 mb-3">{exec.action_taken}</p>
                  {exec.verification_proof && (
                    <div className="text-sm text-gray-500 bg-black/30 p-3 rounded">
                      <div className="font-medium mb-1">Verification:</div>
                      <div>{exec.verification_proof}</div>
                    </div>
                  )}
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No execution logs yet</p>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RequestDetail;
