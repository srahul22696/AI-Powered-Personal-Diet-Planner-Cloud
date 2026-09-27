import React, { useEffect, useState } from "react";
import { api } from "../services/api.js";

const empty = {
  age: "", height_cm: "", weight_kg: "", activity_level: "sedentary",
  dietary_preference: "vegetarian", goal: "maintenance",
};

export default function Profile() {
  const [form, setForm] = useState(empty);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProfile()
      .then((p) => setForm({
        age: p.age ?? "", height_cm: p.height_cm ?? "", weight_kg: p.weight_kg ?? "",
        activity_level: p.activity_level || "sedentary",
        dietary_preference: p.dietary_preference || "vegetarian",
        goal: p.goal || "maintenance",
      }))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaved(false);
    try {
      await api.updateProfile({
        age: Number(form.age), height_cm: Number(form.height_cm), weight_kg: Number(form.weight_kg),
        activity_level: form.activity_level, dietary_preference: form.dietary_preference, goal: form.goal,
      });
      setSaved(true);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p className="loading-state">Getting your profile ready...</p>;

  return (
    <div className="card form-card profile-card">
      <p className="eyebrow">A few things about you</p>
      <h2>Make it your own.</h2>
      <p className="subtitle">Your details help shape meal ideas around your routine and preferences. This demo is not for medical diagnosis.</p>
      <form onSubmit={handleSubmit}>
        <div className="grid-2">
          <div>
            <label htmlFor="profile-age">Age</label>
            <input id="profile-age" type="number" name="age" value={form.age} onChange={handleChange} min={1} max={120} required />
          </div>
          <div>
            <label htmlFor="profile-height">Height (cm)</label>
            <input id="profile-height" type="number" name="height_cm" value={form.height_cm} onChange={handleChange} min={50} max={260} required />
          </div>
        </div>
        <div className="grid-2">
          <div>
            <label htmlFor="profile-weight">Weight (kg)</label>
            <input id="profile-weight" type="number" name="weight_kg" value={form.weight_kg} onChange={handleChange} min={20} max={400} required />
          </div>
          <div>
            <label htmlFor="profile-activity">Activity level</label>
            <select id="profile-activity" name="activity_level" value={form.activity_level} onChange={handleChange}>
              <option value="sedentary">Sedentary</option>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="active">Active</option>
            </select>
          </div>
        </div>
        <div className="grid-2">
          <div>
            <label htmlFor="profile-diet">Dietary preference</label>
            <select id="profile-diet" name="dietary_preference" value={form.dietary_preference} onChange={handleChange}>
              <option value="vegetarian">Vegetarian</option>
              <option value="vegan">Vegan</option>
              <option value="non_vegetarian">Non-Vegetarian</option>
            </select>
          </div>
          <div>
            <label htmlFor="profile-goal">Your focus</label>
            <select id="profile-goal" name="goal" value={form.goal} onChange={handleChange}>
              <option value="maintenance">General balanced eating</option>
              <option value="weight_loss">Weight-management demo</option>
              <option value="weight_gain">Fitness-oriented demo</option>
            </select>
          </div>
        </div>

        {error && <p className="error-text">{error}</p>}
        {saved && <p className="success-text">Your profile is saved. Meal ideas can now feel more like yours.</p>}

        <button type="submit">Save Profile</button>
      </form>
    </div>
  );
}
