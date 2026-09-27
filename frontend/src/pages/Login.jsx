import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, setToken } from "../services/api.js";
import { useAuth } from "../App.jsx";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.login(form.email, form.password);
      setToken(data.access_token);
      login(data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card form-card">
      <p className="eyebrow">Welcome back</p>
      <h2>Come on in.</h2>
      <p className="subtitle">Your meal ideas are right where you left them.</p>
      <form onSubmit={handleSubmit}>
        <label htmlFor="login-email">Email</label>
        <input id="login-email" type="email" name="email" autoComplete="email" value={form.email} onChange={handleChange} required />

        <label htmlFor="login-password">Password</label>
        <input id="login-password" type="password" name="password" autoComplete="current-password" value={form.password} onChange={handleChange} required />

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={loading} style={{ width: "100%" }}>
          {loading ? "Just a moment..." : "Log in to your account"}
        </button>
      </form>
      <p className="form-footer">
        New around here? <Link to="/register">Make an account</Link>
      </p>
    </div>
  );
}
