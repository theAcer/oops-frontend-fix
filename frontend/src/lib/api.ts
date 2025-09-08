import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
console.log(`[API Service] Initializing with API_BASE_URL: ${API_BASE_URL}`); // Added log

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log(`[API Interceptor] Adding Authorization header for: ${config.url}`); // Added log
    } else {
      console.log(`[API Interceptor] No access token found for: ${config.url}`); // Added log
    }
    return config;
  },
  (error) => {
    console.error(`[API Interceptor] Request error:`, error); // Added log
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`[API Service] Response received for ${response.config.url}:`, response.status); // Added log
    return response;
  },
  (error) => {
    console.error(`[API Service] Error response for ${error.config?.url}:`, error.response?.status, error.response?.data); // Added log
    return Promise.reject(error);
  }
);

export default api;