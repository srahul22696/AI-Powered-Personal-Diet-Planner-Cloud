import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../App.jsx";

export default function Landing() {
  const { user } = useAuth();

  return (
    <>
      <section className="landing-hero">
        <div className="hero-copy">
          <p className="eyebrow">A gentler way to eat well</p>
          <h1>Make room for <em>good food.</em></h1>
          <p>
            Thoughtful meal plans shaped around your routine, preferences, and goals.
            Less second-guessing. More good things on your plate.
          </p>
          <div className="hero-actions">
            {user ? (
              <Link className="button" to="/dashboard">Go to your kitchen <span aria-hidden="true">↗</span></Link>
            ) : (
              <>
                <Link className="button" to="/register">Build my meal plan <span aria-hidden="true">↗</span></Link>
                <Link className="button secondary" to="/login">I have an account</Link>
              </>
            )}
          </div>
          <div className="hero-note"><span className="hero-note-mark" aria-hidden="true">✓</span> Simple ideas, tailored to the way you eat</div>
        </div>
        <div className="hero-art" role="img" aria-label="Illustration of a colorful balanced meal on a ceramic plate">
          <div className="art-chip one"><span className="chip-dot" /> A little of everything</div>
          <div className="plate"><div className="plate-food" /></div>
          <div className="art-chip two"><span className="chip-dot" /> Made for your day</div>
          <span className="hero-caption">Good food, made personal</span>
        </div>
      </section>

      <section className="feature-strip" aria-label="What you can do">
        <div className="feature-item">
          <span className="feature-icon" aria-hidden="true">✳</span>
          <span><strong>Made around you</strong><span>Your preferences and everyday goals guide each plan.</span></span>
        </div>
        <div className="feature-item">
          <span className="feature-icon" aria-hidden="true">↗</span>
          <span><strong>Easy to come back to</strong><span>Keep your meal ideas together and revisit them anytime.</span></span>
        </div>
        <div className="feature-item">
          <span className="feature-icon" aria-hidden="true">♡</span>
          <span><strong>Wellbeing, without pressure</strong><span>Friendly inspiration for balanced everyday eating.</span></span>
        </div>
      </section>

      <p className="disclaimer" style={{ marginTop: 24 }}>
        This project uses synthetic/demo data. Generated plans are general educational wellness examples, not medical or clinical nutrition advice.
      </p>
    </>
  );
}
