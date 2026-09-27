import React, { useState, useEffect, createContext, useContext } from "react";
import { Routes, Route, Navigate, Link, NavLink, useNavigate } from "react-router-dom";

import Landing from "./pages/Landing.jsx";
import Register from "./pages/Register.jsx";
import Login from "./pages/Login.jsx";
import Profile from "./pages/Profile.jsx";
import GeneratePlan from "./pages/GeneratePlan.jsx";
import PlanResult from "./pages/PlanResult.jsx";
import SavedPlans from "./pages/SavedPlans.jsx";
import Files from "./pages/Files.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import { clearToken } from "./services/api.js";

export const AuthContext = createContext(null);
export function useAuth() {
  return useContext(AuthContext);
}

function RequireAuth({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="navbar">
      <Link to="/" className="brand">
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none"><path d="M19.5 4.5c-7.8.2-12.2 2.9-12.7 8.1-.3 2.9 1.8 5.1 4.8 4.7 5.2-.6 7.9-5 7.9-12.8Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round"/><path d="M4.2 20c2.8-5.1 6.4-8.1 11-10.4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"/></svg>
        </span>
        <span>Goodfood <span style={{ color: "#82917f", fontWeight: 500 }}>studio</span></span>
      </Link>
      <nav>
        {user ? (
          <>
            <NavLink className="nav-link" to="/dashboard">Home</NavLink>
            <NavLink className="nav-link" to="/generate-plan">Meal plan</NavLink>
            <NavLink className="nav-link" to="/saved-plans">Your plans</NavLink>
            <NavLink className="nav-link" to="/files">Files</NavLink>
            <NavLink className="nav-link" to="/profile">Profile</NavLink>
            <button className="secondary small nav-logout" onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <NavLink className="nav-link" to="/login">Log in</NavLink>
            <Link to="/register" className="button small nav-register">
              Get started
            </Link>
          </>
        )}
      </nav>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else localStorage.removeItem("user");
  }, [user]);

  const login = (userObj) => setUser(userObj);
  const logout = () => {
    clearToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="app-shell">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
            <Route path="/generate-plan" element={<RequireAuth><GeneratePlan /></RequireAuth>} />
            <Route path="/plan-result/:planId" element={<RequireAuth><PlanResult /></RequireAuth>} />
            <Route path="/saved-plans" element={<RequireAuth><SavedPlans /></RequireAuth>} />
            <Route path="/files" element={<RequireAuth><Files /></RequireAuth>} />
            <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        <footer className="app-footer">A little more care in every meal. Made for everyday wellbeing.</footer>
      </div>
    </AuthContext.Provider>
  );
}
