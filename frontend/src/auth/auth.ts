import axios from "axios";
import { toast } from "react-toastify";

// VITE_API_URL is set at build time via the frontend .env file.
// For local dev it defaults to localhost. For production builds,
// set VITE_API_URL=https://your-backend-url in frontend/.env
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || "An unexpected error occurred.";
    // Don't toast 401s globally if they just redirect to login, but toast 500s and other 400s
    if (error.response?.status !== 401) {
      toast.error(message);
    }
    return Promise.reject(error);
  }
);

export default API;
