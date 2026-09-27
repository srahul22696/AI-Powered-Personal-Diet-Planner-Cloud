import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api.js";

export default function GeneratePlan() {
  const [dietaryPreference, setDietaryPreference] = useState("vegetarian");
  const [goal, setGoal] = useState("maintenance");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const plan = await api.generatePlan(dietaryPreference, goal);
      navigate(`/plan-result/${plan.plan_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card form-card">
      <p className="eyebrow">Your next plate</p>
      <h2>What sounds right for you?</h2>
      <p className="subtitle">Choose a food preference and the kind of everyday support you’re looking for.</p>
      <form onSubmit={handleGenerate}>
        <label htmlFor="plan-preference">How do you like to eat?</label>
        <select id="plan-preference" value={dietaryPreference} onChange={(e) => setDietaryPreference(e.target.value)}>
          <option value="vegetarian">Vegetarian</option>
          <option value="vegan">Vegan</option>
          <option value="non_vegetarian">Non-Vegetarian</option>
        </select>

        <label htmlFor="plan-goal">What’s your focus?</label>
        <select id="plan-goal" value={goal} onChange={(e) => setGoal(e.target.value)}>
          <option value="maintenance">General balanced eating</option>
          <option value="weight_loss">Weight-management demo</option>
          <option value="weight_gain">Fitness-oriented demo</option>
        </select>

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={loading} style={{ width: "100%" }}>
          {loading ? "Putting your plan together..." : "Create my meal plan"}
        </button>
      </form>
      <p className="form-footer">Personalized ideas for general wellbeing, not medical nutrition advice.</p>
    </div>
  );
}
