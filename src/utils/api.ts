// API configuration utility
// Vite uses import.meta.env for environment variables
// We have configured vite to make VUE_APP_API_URL available
const API_URL = import.meta.env.VUE_APP_API_URL || 'http://127.0.0.1:8000';

export default {
  baseURL: API_URL,
  API_URL: API_URL, // Adding API_URL for backward compatibility
  // Add other API configuration as needed
}
