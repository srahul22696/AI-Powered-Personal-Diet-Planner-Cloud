import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, downloadAuthedFile } from "../services/api.js";

function MealCard({ slot, meal, number }) {
  if (!meal) return null;
  return (
    <article className="meal-card">
      <div className="meal-heading">
        <div><span className="meal-number">{number}</span><span className="meal-slot">{slot}</span></div>
        <span className="meal-kcal">{meal.kcal} kcal</span>
      </div>
      <strong>{meal.name}</strong>
      <div className="meal-macros">
        <span>Protein <b>{meal.protein_g}g</b></span>
        <span>Carbs <b>{meal.carbs_g}g</b></span>
        <span>Fat <b>{meal.fat_g}g</b></span>
      </div>
    </article>
  );
}

export default function PlanResult() {
  const { planId } = useParams();
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getPlan(planId).then(setPlan).catch((e) => setError(e.message));
  }, [planId]);

  if (error) return <p className="error-text">{error}</p>;
  if (!plan) return <p className="loading-state">Setting the table...</p>;

  const summary = plan.nutrition_summary || {};
  const macros = [
    ["Energy", summary.total_kcal, "kcal"],
    ["Protein", summary.total_protein_g, "g"],
    ["Carbs", summary.total_carbs_g, "g"],
    ["Fat", summary.total_fat_g, "g"],
  ];

  return (
    <div className="plan-page">
      <div className="page-heading plan-page-heading">
        <p className="eyebrow">A day made for you</p>
        <div className="plan-title-line">
          <h1>Your meal plan.</h1>
          <span className="badge-source">{plan.source === "ai_api" ? "Personalized suggestion" : "Thoughtfully put together"}</span>
        </div>
        <p className="subtitle">A flexible starting point for a day of satisfying meals.</p>
      </div>

      <div className="plan-layout">
        <section aria-label="Meals for the day">
          <MealCard slot="Breakfast" meal={plan.breakfast} number="01" />
          <MealCard slot="Lunch" meal={plan.lunch} number="02" />
          <MealCard slot="Snack" meal={plan.snack} number="03" />
          <MealCard slot="Dinner" meal={plan.dinner} number="04" />
        </section>

        <aside>
          <div className="card nutrition-summary">
            <p className="eyebrow">A little overview</p>
            <h3>Your daily nourishment</h3>
            <div className="macro-grid">
              {macros.map(([label, value, unit]) => (
                <div className="macro-item" key={label}><span>{label}</span><strong>{value ?? "—"} {unit}</strong></div>
              ))}
            </div>
            {plan.target_calories && <p className="summary-note">Estimated target from your profile: about {plan.target_calories} kcal.</p>}
            {summary.hydration_reminder && <p className="hydration-note"><span aria-hidden="true">✳</span> {summary.hydration_reminder}</p>}
            <p className="disclaimer">{plan.disclaimer || "General wellness inspiration only. Not medical or clinical nutrition advice."}</p>
          </div>
          <div className="plan-actions">
            <button className="secondary" onClick={() => downloadAuthedFile(api.exportPlanUrl(plan.plan_id), `diet_plan_${plan.plan_id}.txt`)}>Download this plan</button>
            <Link className="button" to="/saved-plans">Browse saved plans</Link>
          </div>
        </aside>
      </div>
    </div>
  );
}
