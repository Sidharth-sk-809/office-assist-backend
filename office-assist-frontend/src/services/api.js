import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  const response = await api.get('/');
  return response.data;
};

// Resume classification
export const classifyResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/classify', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Chat with RAG
export const sendChatMessage = async (userInput, conversationId = null) => {
  const response = await api.post('/chat', {
    user_input: userInput,
    conversation_id: conversationId,
  });
  return response.data;
};

// Submit task
export const submitTask = async (taskText, file = null, employee = null) => {
  const formData = new FormData();
  if (taskText) {
    formData.append('task_text', taskText);
  }
  if (file) {
    formData.append('file', file);
  }
  if (employee?.id) {
    formData.append('employee_id', employee.id);
  }
  if (employee?.name) {
    formData.append('employee_name', employee.name);
  }
  
  const response = await api.post('/submit-task', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Upload training material
export const uploadMaterial = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload-material', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getScenarios = async (params = {}) => {
  const response = await api.get('/scenarios', { params });
  return response.data;
};

export const getScenarioDetail = async (scenarioId) => {
  const response = await api.get(`/scenarios/${scenarioId}`);
  return response.data;
};

export const submitScenarioSolution = async (scenarioId, payload) => {
  const response = await api.post(`/scenarios/${scenarioId}/submit`, {
    scenario_id: scenarioId,
    ...payload,
  });
  return response.data;
};

export const getEmployeeProgress = async (employeeId) => {
  const response = await api.get(`/employee/${employeeId}/progress`);
  return response.data;
};

export default api;
