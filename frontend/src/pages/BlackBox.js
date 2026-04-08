import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, Code, Scale, AlertTriangle, Users, Activity, Lock } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/blackbox`;

const BlackBox = () => {
  const [accessKey, setAccessKey] = useState(localStorage.getItem('blackbox_key') || '');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [dashboard, setDashboard] = useState(null);
  const [codeSubmissions, setCodeSubmissions] = useState([]);
  const [ethicsCases, setEthicsCases] = useState([]);
  const [taskArbitrations, setTaskArbitrations] = useState([]);
  const [controllers, setControllers] = useState([]);

  const axiosConfig = {
    headers: {
      'X-Blackbox-Key': accessKey
    }
  };

  const handleLogin = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`, axiosConfig);
      setDashboard(response.data);
      setIsAuthenticated(true);
      localStorage.setItem('blackbox_key', accessKey);
    } catch (error) {
      alert('Invalid Black Box access key');
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchAllData();
    }
  }, [isAuthenticated]);

  const fetchAllData = async () => {
    try {
      const [dashRes, codeRes, ethicsRes, tasksRes, controllersRes] = await Promise.all([
        axios.get(`${API}/dashboard`, axiosConfig),
        axios.get(`${API}/code-submissions?status=pending`, axiosConfig),
        axios.get(`${API}/ethics-cases?pending_only=true`, axiosConfig),
        axios.get(`${API}/task-arbitrations?pending_only=true`, axiosConfig),
        axios.get(`${API}/controllers`, axiosConfig).catch(() => ({ data: [] })) // Might fail if not master
      ]);

      setDashboard(dashRes.data);
      setCodeSubmissions(codeRes.data);
      setEthicsCases(ethicsRes.data);
      setTaskArbitrations(tasksRes.data);
      setControllers(controllersRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleCodeReview = async (submissionId, status, comments) => {
    try {
      await axios.patch(`${API}/code-submissions/${submissionId}`, {
        status,
        comments
      }, axiosConfig);
      
      fetchAllData();
      alert(`Code ${status}`);
    } catch (error) {
      alert('Error submitting review');
    }
  };

  const handleEthicsDecision = async (caseId, decision, rationale) => {
    try {
      await axios.patch(`${API}/ethics-cases/${caseId}`, {
        decision,
        rationale
      }, axiosConfig);
      
      fetchAllData();
      alert(`Ethics case ${decision}`);
    } catch (error) {
      alert('Error deciding ethics case');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <Card className="max-w-md w-full bg-gray-900 border-red-900 p-8">
          <div className="text-center mb-6">
            <Shield size={64} className="mx-auto mb-4 text-red-500" />
            <h1 className="text-3xl font-light mb-2 text-gray-100">THE BLACK BOX</h1>
            <p className="text-gray-500 text-sm">Master Control System</p>
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="key" className="text-gray-300">Access Key</Label>
              <Input
                id="key"
                type="password"
                value={accessKey}
                onChange={(e) => setAccessKey(e.target.value)}
                className="bg-black border-gray-700 text-gray-100"
                placeholder="Enter Black Box key"
              />
            </div>

            <Button
              onClick={handleLogin}
              className="w-full bg-red-600 hover:bg-red-700"
            >
              <Lock size={16} className="mr-2" />
              Authenticate
            </Button>
          </div>

          <p className="text-xs text-gray-700 mt-6 text-center">
            Unauthorized access is prohibited and logged.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Shield size={32} className="text-red-500" />
              <div>
                <h1 className="text-3xl font-light">THE BLACK BOX</h1>
                <p className="text-sm text-gray-500">Master Control System</p>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={() => {
                setIsAuthenticated(false);
                localStorage.removeItem('blackbox_key');
              }}
              className="border-red-900 text-red-500"
            >
              Logout
            </Button>
          </div>

          {/* Dashboard Metrics */}
          {dashboard && (
            <div className="grid grid-cols-4 gap-4">
              <Card className="bg-gray-900/50 border-gray-800 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Code size={20} className="text-blue-400" />
                  <span className="text-sm text-gray-400">Code Review</span>
                </div>
                <div className="text-2xl font-light">{dashboard.code_review.pending}</div>
                <div className="text-xs text-gray-600">Pending</div>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Scale size={20} className="text-purple-400" />
                  <span className="text-sm text-gray-400">Ethics</span>
                </div>
                <div className="text-2xl font-light">{dashboard.ethics.pending}</div>
                <div className="text-xs text-gray-600">Pending</div>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle size={20} className="text-orange-400" />
                  <span className="text-sm text-gray-400">Tasks</span>
                </div>
                <div className="text-2xl font-light">{dashboard.tasks.pending}</div>
                <div className="text-xs text-gray-600">Need Arbitration</div>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Activity size={20} className="text-green-400" />
                  <span className="text-sm text-gray-400">Platform</span>
                </div>
                <div className="text-2xl font-light">{dashboard.platform.total_users}</div>
                <div className="text-xs text-gray-600">Total Users</div>
              </Card>
            </div>
          )}
        </div>

        {/* Tabs */}
        <Tabs defaultValue="code" className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900/50">
            <TabsTrigger value="code">Code Review ({codeSubmissions.length})</TabsTrigger>
            <TabsTrigger value="ethics">Ethics ({ethicsCases.length})</TabsTrigger>
            <TabsTrigger value="tasks">Tasks ({taskArbitrations.length})</TabsTrigger>
            <TabsTrigger value="controllers">Controllers ({controllers.length})</TabsTrigger>
          </TabsList>

          {/* Code Review Tab */}
          <TabsContent value="code" className="space-y-4 mt-6">
            {codeSubmissions.length > 0 ? (
              codeSubmissions.map((submission) => (
                <Card key={submission.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-normal mb-1">{submission.contributor_github}</h3>
                      <p className="text-sm text-gray-500">PR #{submission.pr_number || 'N/A'}</p>
                    </div>
                    <div className="text-right">
                      <Badge className={`${
                        submission.security_score >= 80 ? 'bg-green-900/30 text-green-400' :
                        submission.security_score >= 60 ? 'bg-yellow-900/30 text-yellow-400' :
                        'bg-red-900/30 text-red-400'
                      }`}>
                        Security: {submission.security_score}/100
                      </Badge>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="text-sm text-gray-400 mb-2">Files Changed:</div>
                    <div className="flex flex-wrap gap-2">
                      {submission.files_changed.map((file, i) => (
                        <Badge key={i} variant="outline" className="text-xs">{file}</Badge>
                      ))}
                    </div>
                  </div>

                  {submission.security_issues.length > 0 && (
                    <div className="mb-4 p-4 bg-red-900/20 rounded border border-red-900/50">
                      <div className="text-sm font-medium text-red-400 mb-2">Security Issues:</div>
                      <ul className="text-xs text-gray-400 space-y-1">
                        {submission.security_issues.map((issue, i) => (
                          <li key={i}>• {issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {submission.ai_review_summary && (
                    <div className="mb-4 p-4 bg-gray-800/50 rounded">
                      <div className="text-sm font-medium text-gray-300 mb-2">AI Review:</div>
                      <p className="text-xs text-gray-400 whitespace-pre-wrap">{submission.ai_review_summary}</p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      onClick={() => {
                        const comments = prompt('Review comments:');
                        if (comments) handleCodeReview(submission.id, 'approved', comments);
                      }}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      Approve
                    </Button>
                    <Button
                      onClick={() => {
                        const comments = prompt('What changes are needed?');
                        if (comments) handleCodeReview(submission.id, 'changes_requested', comments);
                      }}
                      variant="outline"
                    >
                      Request Changes
                    </Button>
                    <Button
                      onClick={() => {
                        const comments = prompt('Reason for rejection:');
                        if (comments) handleCodeReview(submission.id, 'rejected', comments);
                      }}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      Reject
                    </Button>
                  </div>
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-12">No pending code reviews</p>
            )}
          </TabsContent>

          {/* Ethics Tab */}
          <TabsContent value="ethics" className="space-y-4 mt-6">
            {ethicsCases.length > 0 ? (
              ethicsCases.map((ethicsCase) => (
                <Card key={ethicsCase.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <div className="mb-4">
                    <h3 className="text-lg font-normal mb-2">Request ID: {ethicsCase.request_id}</h3>
                    <p className="text-gray-300">{ethicsCase.request_content}</p>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-gray-500">AI Legality</div>
                      <div className="text-lg">{ethicsCase.ai_legality_score}/10</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">AI Morality</div>
                      <div className="text-lg">{ethicsCase.ai_morality_score}/10</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">AI Harm</div>
                      <div className="text-lg">{ethicsCase.ai_harm_score}/10</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Evaluations</div>
                      <div className="text-lg">{ethicsCase.community_evaluation_count}</div>
                    </div>
                  </div>

                  <div className="mb-4 p-3 bg-yellow-900/20 rounded border border-yellow-900/50">
                    <div className="text-sm text-yellow-400">Reason for Review: {ethicsCase.reason}</div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => {
                        const rationale = prompt('Why approve this request?');
                        if (rationale) handleEthicsDecision(ethicsCase.id, 'approve', rationale);
                      }}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      Approve
                    </Button>
                    <Button
                      onClick={() => {
                        const rationale = prompt('Why reject this request?');
                        if (rationale) handleEthicsDecision(ethicsCase.id, 'reject', rationale);
                      }}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      Reject
                    </Button>
                    <Button
                      onClick={() => {
                        const rationale = prompt('What information is needed?');
                        if (rationale) handleEthicsDecision(ethicsCase.id, 'request_more_info', rationale);
                      }}
                      variant="outline"
                    >
                      Request More Info
                    </Button>
                  </div>
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-12">No pending ethics cases</p>
            )}
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="space-y-4 mt-6">
            {taskArbitrations.length > 0 ? (
              taskArbitrations.map((task) => (
                <Card key={task.id} className="bg-gray-900/50 border-gray-800 p-6">
                  <div className="mb-4">
                    <Badge className="mb-2">{task.issue_type}</Badge>
                    <p className="text-gray-300">{task.description}</p>
                  </div>

                  {task.suggested_actions.length > 0 && (
                    <div className="mb-4">
                      <div className="text-sm text-gray-400 mb-2">Suggested Actions:</div>
                      <ul className="text-sm text-gray-500 space-y-1">
                        {task.suggested_actions.map((action, i) => (
                          <li key={i}>• {action}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <Button
                    onClick={() => {
                      const notes = prompt('Resolution notes:');
                      if (notes) {
                        // Handle task resolution
                        alert('Task resolution feature coming soon');
                      }
                    }}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Resolve Task
                  </Button>
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-12">No tasks need arbitration</p>
            )}
          </TabsContent>

          {/* Controllers Tab */}
          <TabsContent value="controllers" className="space-y-4 mt-6">
            <Card className="bg-gray-900/50 border-gray-800 p-6">
              <h3 className="text-lg font-normal mb-4">Active Controllers</h3>
              {controllers.length > 0 ? (
                <div className="space-y-3">
                  {controllers.map((controller) => (
                    <div key={controller.id} className="flex items-center justify-between p-4 bg-gray-800/50 rounded">
                      <div>
                        <div className="font-medium">{controller.name}</div>
                        <div className="text-sm text-gray-500">{controller.email}</div>
                        <div className="flex gap-2 mt-2">
                          {controller.permissions.map((perm, i) => (
                            <Badge key={i} variant="outline" className="text-xs">{perm}</Badge>
                          ))}
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        className="border-red-900 text-red-500"
                        onClick={() => {
                          if (confirm('Revoke controller access?')) {
                            // Handle revoke
                          }
                        }}
                      >
                        Revoke
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No controllers assigned</p>
              )}
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default BlackBox;
