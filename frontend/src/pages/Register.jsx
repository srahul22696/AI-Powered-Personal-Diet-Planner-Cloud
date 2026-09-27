import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, setToken } from "../services/api.js";
import { useAuth } from "../App.jsx";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
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
      const data = await api.register(form.name, form.email, form.password);
      setToken(data.access_token);
      login(data.user);
      navigate("/profile");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card form-card">
      <p className="eyebrow">A fresh start</p>
      <h2>Let’s make eating well easier.</h2>
      <p className="subtitle">Create your space for personal meal ideas and plans.</p>
      <form onSubmit={handleSubmit}>
        <label htmlFor="register-name">Full name</label>
        <input id="register-name" name="name" autoComplete="name" value={form.name} onChange={handleChange} required />

        <label htmlFor="register-email">Email</label>
        <input id="register-email" type="email" name="email" autoComplete="email" value={form.email} onChange={handleChange} required />

        <label htmlFor="register-password">Password</label>
        <input id="register-password" type="password" name="password" autoComplete="new-password" value={form.password} onChange={handleChange} minLength={8} required />

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={loading} style={{ width: "100%" }}>
          {loading ? "Preparing your space..." : "Create my account"}
        </button>
      </form>
      <p className="form-footer">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
