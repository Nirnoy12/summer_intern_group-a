import { Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Landing from "./landing/LandingPage";
import Dashboard from "./dashboard/DashboardPage";
import CoursePlayer from "./course-player/CoursePlayerPage";
import Login from "./auth/LoginPage";
import Register from "./auth/RegisterPage";

import { useAuth } from "./auth/AuthContext";

function App() {
  const { token } = useAuth();

  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} theme="dark" />
      <Routes>
        {/* Public Landing Page */}
        <Route
          path="/"
          element={<Landing />}
        />

        {/* Auth Pages */}
        <Route
          path="/login"
          element={
            token ? <Navigate to="/dashboard" replace /> : <Login />
          }
        />

        <Route
          path="/register"
          element={
            token ? <Navigate to="/dashboard" replace /> : <Register />
          }
        />

        {/* Protected Pages */}
        <Route
          path="/dashboard"
          element={
            token ? (
              <Dashboard />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/playlist/:id"
          element={
            token ? (
              <CoursePlayer />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Catch-all */}
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </>
  );
}

export default App;