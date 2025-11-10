import React, { useState, useEffect } from 'react';
import { auditAPI, agentAPI } from '../services/api';

const AuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [usage, setUsage] = useState(null);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAgents();
    loadLogs();
    loadUsage();
  }, []);

  useEffect(() => {
    if (selectedAgent !== null) {
      loadLogs();
      loadUsage();
    }
  }, [selectedAgent]);

  const loadAgents = async () => {
    try {
      const data = await agentAPI.list();
      setAgents(data.agents || []);
    } catch (err) {
      console.error('Error loading agents:', err);
    }
  };

  const loadLogs = async () => {
    try {
      setLoading(true);
      const filters = selectedAgent ? { agent_id: selectedAgent } : {};
      const data = await auditAPI.getLogs(filters);
      setLogs(data.conversations || []);
    } catch (err) {
      setError(err.message);
      console.error('Error loading logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUsage = async () => {
    try {
      const data = await auditAPI.getUsage(selectedAgent || null);
      setUsage(data);
    } catch (err) {
      console.error('Error loading usage:', err);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Audit Logs</h1>

      {/* Usage Metrics */}
      {usage && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">
              Total Requests
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {usage.request_count}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">
              Total Tokens
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {usage.total_tokens.toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">
              Total Cost
            </h3>
            <p className="text-3xl font-bold text-purple-600">
              ${usage.total_cost_usd.toFixed(4)}
            </p>
          </div>
        </div>
      )}

      {/* Filter and Logs */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Filter by Agent
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Agents</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
        </div>

        <h2 className="text-xl font-semibold mb-4">Conversation History</h2>

        {loading ? (
          <p className="text-gray-500">Loading logs...</p>
        ) : error ? (
          <div className="text-red-600">
            <p>Error loading logs: {error}</p>
            <button
              onClick={loadLogs}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        ) : logs.length === 0 ? (
          <p className="text-gray-500">No conversation logs found.</p>
        ) : (
          <div className="space-y-4">
            {logs.map((log) => (
              <div
                key={log.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <p className="text-sm text-gray-500">
                      {formatDate(log.timestamp)}
                    </p>
                    <p className="text-xs text-gray-400">
                      Agent ID: {log.agent_id.slice(0, 8)}...
                    </p>
                  </div>
                  <div className="text-right text-sm">
                    <span className="text-gray-600">
                      {log.tokens_used} tokens
                    </span>
                    <span className="text-gray-400 ml-3">
                      {log.response_time_ms}ms
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-xs font-semibold text-gray-500 mb-1">
                      USER:
                    </p>
                    <p className="text-gray-800 bg-blue-50 p-3 rounded">
                      {log.user_message}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-gray-500 mb-1">
                      AGENT:
                    </p>
                    <p className="text-gray-800 bg-gray-50 p-3 rounded">
                      {log.agent_response}
                    </p>
                  </div>

                  {log.rag_context && log.rag_context.length > 0 && (
                    <details className="text-sm">
                      <summary className="cursor-pointer text-blue-600 hover:text-blue-700 font-semibold">
                        RAG Context ({log.rag_context.length} documents)
                      </summary>
                      <div className="mt-2 space-y-2 pl-4">
                        {log.rag_context.map((doc, i) => (
                          <div key={i} className="bg-yellow-50 p-2 rounded text-xs">
                            {doc.substring(0, 200)}
                            {doc.length > 200 ? '...' : ''}
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogsPage;
