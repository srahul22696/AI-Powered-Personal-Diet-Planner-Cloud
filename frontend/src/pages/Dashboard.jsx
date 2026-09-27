import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";
import { useAuth } from "../App.jsx";

const pretty = (value) => (value || "").replaceAll("_", " ");

export default function Dashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [plans, setPlans] = useState([]);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getProfile(), api.listPlans(), api.listFiles()])
      .then(([p, pl, f]) => { setProfile(p); setPlans(pl); setFiles(f); })
      .catch((e) => setError(e.message));
  }, []);

  const latestPlan = plans[0];
  const firstName = user?.name?.trim().split(/\s+/)[0] || "friend";

  return (
    <>
      <div className="dashboard-welcome">
        <div>
          <p className="eyebrow">Your little corner of good food</p>
          <h1>Welcome back, {firstName}.</h1>
          <p className="subtitle">A fresh start can be as simple as your next meal.</p>
        </div>
        <Link className="button" to="/generate-plan">Plan my meals <span aria-hidden="true">↗</span></Link>
      </div>
      {error && <p className="error-text">{error}</p>}

      <section className="dashboard-grid" aria-label="Your meal planning details">
        <div className="stat-card">
          <span className="stat-label">YOUR FOCUS</span>
          <div className="stat-value">{pretty(profile?.goal) || "Set your goal"}</div>
          <span className="stat-note">A gentle direction for your plans</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">YOUR TABLE</span>
          <div className="stat-value">{pretty(profile?.dietary_preference) || "Add a preference"}</div>
          <span className="stat-note">Meals that fit how you like to eat</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">IN YOUR RECIPE BOX</span>
          <div className="stat-value">{plans.length} {plans.length === 1 ? "plan" : "plans"}</div>
          <span className="stat-note">Saved for whenever you need an idea</span>
        </div>
      </section>

      <section className="dashboard-feature">
        <div>
          <p className="eyebrow">Your next good thing</p>
          <h2>{latestPlan ? "Pick up where you left off." : "A good plan starts with you."}</h2>
          <p>{latestPlan ? "Your latest meal plan is ready whenever you are." : "Tell us a little about how you eat, and we’ll put together a plan to get you started."}</p>
          <Link className="button" to={latestPlan ? `/plan-result/${latestPlan.plan_id}` : "/profile"}>
            {latestPlan ? "Open latest plan" : "Set up my profile"} <span aria-hidden="true">↗</span>
          </Link>
        </div>
        <div className="feature-ornament" aria-hidden="true">g</div>
      </section>

      <div className="dashboard-lower">
        <section className="card">
          <div className="section-title">
            <h3>Your latest plate</h3>
            {latestPlan && <Link className="text-link" to={`/plan-result/${latestPlan.plan_id}`}>See the whole plan ↗</Link>}
          </div>
          {latestPlan ? (
            <div className="latest-meals">
              {[["Breakfast", latestPlan.breakfast], ["Lunch", latestPlan.lunch], ["Dinner", latestPlan.dinner]].map(([slot, meal]) => (
                <div className="mini-meal" key={slot}><span>{slot}</span><strong>{meal?.name || "A meal to discover"}</strong></div>
              ))}
            </div>
          ) : (
            <div className="empty-state">Your first meal plan will show up here. Start with your preferences and we’ll take it from there.</div>
          )}
        </section>
        <section className="card">
          <div className="section-title"><h3>Quick paths</h3></div>
          <div className="quick-links">
            <Link className="quick-link" to="/saved-plans"><span>Browse saved plans <small className="muted">· {plans.length}</small></span><span aria-hidden="true">↗</span></Link>
            <Link className="quick-link" to="/files"><span>Your uploaded files <small className="muted">· {files.length}</small></span><span aria-hidden="true">↗</span></Link>
            <Link className="quick-link" to="/profile"><span>Update your profile</span><span aria-hidden="true">↗</span></Link>
          </div>
        </section>
      </div>
    </>
  );
}
