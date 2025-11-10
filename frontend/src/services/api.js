/**
 * API client service
 * Handles all HTTP requests to the backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data?.error || {};
      console.error('API Error:', errorData);
      throw new Error(errorData.message || 'An error occurred');
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
      throw new Error('Network error. Please check your connection.');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw new Error(error.message);
    }
  }
);

// ===================================================================
// AGENT ENDPOINTS
// ===================================================================

export const agentAPI = {
  /**
   * Create a new agent
   */
  create: async (data) => {
    const response = await api.post('/agents/create', data);
    return response.data;
  },

  /**
   * List all agents
   */
  list: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await api.get(`/agents?${params}`);
    return response.data;
  },

  /**
   * Get agent by ID
   */
  get: async (agentId) => {
    const response = await api.get(`/agents/${agentId}`);
    return response.data;
  },

  /**
   * Update agent
   */
  update: async (agentId, data) => {
    const response = await api.put(`/agents/${agentId}`, data);
    return response.data;
  },

  /**
   * Delete agent
   */
  delete: async (agentId) => {
    const response = await api.delete(`/agents/${agentId}`);
    return response.data;
  },

  /**
   * Get agent status
   */
  getStatus: async (agentId) => {
    const response = await api.get(`/agents/${agentId}/status`);
    return response.data;
  },
};

// ===================================================================
// CHAT ENDPOINTS
// ===================================================================

export const chatAPI = {
  /**
   * Send message to agent
   */
  sendMessage: async (agentId, message, stream = false) => {
    const response = await api.post(`/agents/${agentId}/chat`, {
      message,
      stream,
    });
    return response.data;
  },
};

// ===================================================================
// RAG ENDPOINTS
// ===================================================================

export const ragAPI = {
  /**
   * Upload knowledge base file
   */
  uploadDocument: async (agentId, file) => {
    const formData = new FormData();
    formData.append('agent_id', agentId);
    formData.append('file', file);

    const response = await api.post('/rag/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * List knowledge base documents
   */
  listDocuments: async (agentId) => {
    const response = await api.get(`/rag/documents/${agentId}`);
    return response.data;
  },

  /**
   * Delete knowledge base document
   */
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/rag/documents/${documentId}`);
    return response.data;
  },
};

// ===================================================================
// AUDIT ENDPOINTS
// ===================================================================

export const auditAPI = {
  /**
   * Get conversation logs
   */
  getLogs: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await api.get(`/audit/logs?${params}`);
    return response.data;
  },

  /**
   * Get API usage metrics
   */
  getUsage: async (agentId = null) => {
    const url = agentId ? `/audit/usage?agent_id=${agentId}` : '/audit/usage';
    const response = await api.get(url);
    return response.data;
  },

  /**
   * Export logs as JSON
   */
  exportLogs: async (agentId = null) => {
    const url = agentId ? `/audit/export?agent_id=${agentId}` : '/audit/export';
    const response = await api.get(url);
    return response.data;
  },
};

// ===================================================================
// HEALTH CHECK
// ===================================================================

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
