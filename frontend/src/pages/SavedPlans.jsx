import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";

export default function SavedPlans() {
  const [plans, setPlans] = useState([]);
  const [error, setError] = useState("");

  const load = () => api.listPlans().then(setPlans).catch((e) => setError(e.message));

  useEffect(() => { load(); }, []);

  const handleDelete = async (planId) => {
    try {
      await api.deletePlan(planId);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">Your recipe box</p>
        <h1>Plans to come back to.</h1>
        <p className="subtitle">Keep the meal ideas you like close at hand.</p>
      </div>
      <div className="card content-card">
      {error && <p className="error-text">{error}</p>}
      {plans.length === 0 && <div className="empty-state">No meal plans here just yet. Create one and it’ll be ready when you need a little inspiration.</div>}

      {plans.map((p) => (
        <div className="list-row" key={p.plan_id}>
          <div>
            <strong>{new Date(p.created_at).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" })}</strong>
            <div className="subtitle" style={{ margin: 0 }}>
              {p.breakfast?.name || "Meal plan"} {p.lunch?.name ? `· ${p.lunch.name}` : ""}
            </div>
          </div>
          <div className="row-actions">
            <Link className="button secondary small" to={`/plan-result/${p.plan_id}`}>Open plan</Link>
            <button className="danger small" onClick={() => handleDelete(p.plan_id)}>Delete</button>
          </div>
        </div>
      ))}

      <div style={{ marginTop: 22 }}><Link className="button" to="/generate-plan">Create a new plan <span aria-hidden="true">↗</span></Link></div>
      </div>
    </>
  );
}
