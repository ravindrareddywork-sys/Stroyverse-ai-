/**
 * StoryVerse AI — API Client (api.js)
 * Reusable HTTP client communicating with the Flask backend.
 */

(function () {
  'use strict';

  // Supplied by js/config.js before this API client is loaded.
  const API_BASE_URL = window.STORYVERSE_API_URL;
  if (!API_BASE_URL) {
    throw new Error('STORYVERSE_API_URL must be configured before loading the API client.');
  }

  // In-flight GET request deduplication cache
  const inFlightGetRequests = new Map();

  /**
   * Generic request wrapper around fetch() with standard error handling.
   * Features:
   *   - In-flight GET request deduplication (prevents duplicate rapid requests)
   *   - Graceful 429 Rate-Limit detection with Retry-After header parsing
   *   - Safe non-JSON error response handling
   * @param {string} endpoint - Path relative to /api (e.g. '/health' or '/projects')
   * @param {object} options - Fetch options (method, headers, body, etc.)
   * @returns {Promise<object>} JSON response object
   */
  async function apiRequest(endpoint, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const url = `${API_BASE_URL}/api${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

    // Request deduplication for concurrent identical GET requests
    if (method === 'GET' && inFlightGetRequests.has(url)) {
      return inFlightGetRequests.get(url);
    }
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    const execPromise = (async () => {
      try {
        const response = await fetch(url, config);
        let data = null;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
          try {
            data = await response.json();
          } catch {
            data = null;
          }
        }

        if (!response.ok) {
          let msg = data?.message;
          const retryHeader = response.headers.get('Retry-After');
          if (response.status === 429) {
            if (retryHeader) {
              msg = `Too many requests. Please wait ${retryHeader} seconds and try again.`;
            } else if (!msg) {
              msg = 'Too many requests. Please wait a moment and try again.';
            }
          }
          if (!msg) {
            msg = `Request failed with status ${response.status}`;
          }

          const error = new Error(msg);
          error.status = response.status;
          error.errors = data?.errors || {};
          if (retryHeader) {
            error.retryAfter = parseInt(retryHeader, 10) || retryHeader;
          }
          throw error;
        }

        return data !== null ? data : { success: true };
      } catch (err) {
        if (err.name === 'TypeError') {
          const connectionError = new Error(
            `Could not connect to the StoryVerse backend at ${API_BASE_URL}. ` +
            'Check that the backend is online and allows requests from this frontend (CORS).'
          );
          connectionError.cause = err;
          console.error(`API Error [${endpoint}]:`, connectionError);
          throw connectionError;
        }
        console.error(`API Error [${endpoint}]:`, err);
        throw err;
      }
    })();

    if (method === 'GET') {
      inFlightGetRequests.set(url, execPromise);
      const clearInFlightRequest = () => {
        inFlightGetRequests.delete(url);
      };
      execPromise.then(clearInFlightRequest, clearInFlightRequest);
    }

    return execPromise;
  }

  /**
   * Probes the backend health check endpoint.
   * @returns {Promise<boolean>} True if connected and healthy, false otherwise.
   */
  async function checkHealth() {
    try {
      const result = await apiRequest('/health', { method: 'GET' });
      return result && result.success === true && result.data?.status === 'healthy';
    } catch (err) {
      return false;
    }
  }

  /**
   * Story Generation & Editing Endpoints (Phase 5)
   */
  async function generateStory(params) {
    return apiRequest('/generate-story', {
      method: 'POST',
      body: params
    });
  }

  async function regenerateStory(params) {
    return apiRequest('/regenerate', {
      method: 'POST',
      body: params
    });
  }

  async function expandStory(params) {
    return apiRequest('/expand', {
      method: 'POST',
      body: params
    });
  }

  async function shortenStory(params) {
    return apiRequest('/shorten', {
      method: 'POST',
      body: params
    });
  }

  async function continueStory(params) {
    return apiRequest('/continue', {
      method: 'POST',
      body: params
    });
  }

  /**
   * Screenplay & Scene Generation Endpoints (Phase 6)
   */
  async function generateScript(params) {
    return apiRequest('/generate-script', {
      method: 'POST',
      body: params
    });
  }

  async function generateScene(params) {
    return apiRequest('/generate-scene', {
      method: 'POST',
      body: params
    });
  }

  /**
   * Character Generation Endpoints (Phase 7)
   */
  async function generateCharacter(params) {
    return apiRequest('/generate-character', {
      method: 'POST',
      body: params
    });
  }

  async function generateCharacterVariations(params) {
    return apiRequest('/generate-character-variations', {
      method: 'POST',
      body: params
    });
  }

  /**
   * AI Writing Assistant Endpoints (Phase 8)
   */
  async function rewriteText(params) {
    return apiRequest('/rewrite', {
      method: 'POST',
      body: params
    });
  }

  async function translateText(params) {
    return apiRequest('/translate', {
      method: 'POST',
      body: params
    });
  }

  async function summarizeText(params) {
    return apiRequest('/summarize', {
      method: 'POST',
      body: params
    });
  }

  async function generateDialogue(params) {
    return apiRequest('/generate-dialogue', {
      method: 'POST',
      body: params
    });
  }

  async function generatePlotTwist(params) {
    return apiRequest('/generate-plot-twist', {
      method: 'POST',
      body: params
    });
  }

  async function continueWriting(params) {
    return apiRequest('/continue-writing', {
      method: 'POST',
      body: params
    });
  }

  /**
   * Project Management & Persistence Endpoints (Phase 9)
   */
  async function createProject(data) {
    return apiRequest('/projects', {
      method: 'POST',
      body: data
    });
  }

  async function getProjects(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.project_type && params.project_type !== 'all') query.append('project_type', params.project_type);
    if (params.genre && params.genre !== 'all') query.append('genre', params.genre);
    if (params.page) query.append('page', params.page);
    if (params.per_page) query.append('per_page', params.per_page);
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.order) query.append('order', params.order);

    const queryString = query.toString();
    const endpoint = queryString ? `/projects?${queryString}` : '/projects';
    return apiRequest(endpoint, { method: 'GET' });
  }

  async function getProject(projectId) {
    return apiRequest(`/projects/${projectId}`, { method: 'GET' });
  }

  async function updateProject(projectId, data) {
    return apiRequest(`/projects/${projectId}`, {
      method: 'PUT',
      body: data
    });
  }

  async function deleteProject(projectId) {
    return apiRequest(`/projects/${projectId}`, {
      method: 'DELETE'
    });
  }

  async function saveProjectVersion(projectId, data) {
    return apiRequest(`/projects/${projectId}/versions`, {
      method: 'POST',
      body: data
    });
  }

  async function getProjectVersions(projectId, order = 'desc') {
    return apiRequest(`/projects/${projectId}/versions?order=${encodeURIComponent(order)}`, {
      method: 'GET'
    });
  }

  async function getProjectVersion(projectId, versionId) {
    return apiRequest(`/projects/${projectId}/versions/${versionId}`, {
      method: 'GET'
    });
  }

  async function restoreProjectVersion(projectId, versionId) {
    return apiRequest(`/projects/${projectId}/versions/${versionId}/restore`, {
      method: 'POST'
    });
  }

  /**
   * Document Export Endpoints (Phase 10)
   * Downloads binary file attachments (TXT, PDF, DOCX) directly to the user's computer.
   */
  async function exportDocument(format, payload) {
    const validFormats = ['txt', 'pdf', 'docx'];
    const fmt = (format || 'txt').toLowerCase();
    if (!validFormats.includes(fmt)) {
      throw new Error(`Unsupported export format '${fmt}'. Choose txt, pdf, or docx.`);
    }

    const url = `${API_BASE_URL}/api/export/${fmt}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errJson = await response.json().catch(() => null);
      throw new Error(errJson?.message || `Export failed with status ${response.status}`);
    }

    const blob = await response.blob();
    const disposition = response.headers.get('Content-Disposition') || '';
    let filename = `StoryVerse_Export.${fmt}`;
    const match = disposition.match(/filename=["']?([^"';]+)["']?/i);
    if (match && match[1]) {
      filename = match[1];
    }

    // Trigger browser file download
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);

    return { success: true, filename };
  }

  // ============================================================
  // RAG (Retrieval-Augmented Generation) API
  // ============================================================

  async function ingestRagDocument(data) {
    return apiRequest('/rag/ingest', {
      method: 'POST',
      body: data
    });
  }

  async function getRagDocuments(params = {}) {
    let query = '';
    if (params.project_id) {
      query = `?project_id=${encodeURIComponent(params.project_id)}`;
    }
    return apiRequest(`/rag/documents${query}`, { method: 'GET' });
  }

  async function getRagDocument(docId) {
    return apiRequest(`/rag/documents/${encodeURIComponent(docId)}`, { method: 'GET' });
  }

  async function deleteRagDocument(docId) {
    return apiRequest(`/rag/documents/${encodeURIComponent(docId)}`, { method: 'DELETE' });
  }

  async function queryRag(params) {
    return apiRequest('/rag/query', {
      method: 'POST',
      body: params
    });
  }

  async function getRagStatus() {
    return apiRequest('/rag/status', { method: 'GET' });
  }

  // Export API Client
  window.StoryVerseAPI = {
    BASE_URL: API_BASE_URL,
    request: apiRequest,
    checkHealth,
    generateStory,
    regenerateStory,
    expandStory,
    shortenStory,
    continueStory,
    generateScript,
    generateScene,
    generateCharacter,
    generateCharacterVariations,
    rewriteText,
    translateText,
    summarizeText,
    generateDialogue,
    generatePlotTwist,
    continueWriting,
    createProject,
    getProjects,
    getProject,
    updateProject,
    deleteProject,
    saveProjectVersion,
    getProjectVersions,
    getProjectVersion,
    restoreProjectVersion,
    exportDocument,
    ingestRagDocument,
    getRagDocuments,
    getRagDocument,
    deleteRagDocument,
    queryRag,
    getRagStatus
  };
})();
