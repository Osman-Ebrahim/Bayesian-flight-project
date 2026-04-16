import numpy as np

def risk_posterior_samples(
    weather_severity: int,
    aircraft_age_years: int,
    maintenance_score: int,
    pilot_hours: int,
    n_samples: int = 5000,
    seed: int = 42,
):
    """
    Bayesian-style risk estimator (PoC).
    Returns a distribution of risk probabilities to represent uncertainty.

    Important:
    - This is an academic proof-of-concept and not calibrated to operational accident rates.
    - The model structure is transparent and designed for later calibration using literature/public datasets.
    """
    rng = np.random.default_rng(seed)

    # Prior: very low base risk (Beta prior)
    alpha_prior = 1.0
    beta_prior = 99.0

    # Convert inputs into a risk "evidence" score
    weather_term = 0.20 * (weather_severity - 1)            # 0..0.8
    age_term = 0.03 * min(aircraft_age_years, 30)           # 0..0.9
    maint_term = -0.08 * (maintenance_score - 5)            # -0.32..0.40 approx
    pilot_term = -0.00008 * min(pilot_hours, 15000)         # 0..-1.2

    evidence = weather_term + age_term + maint_term + pilot_term

    # Add uncertainty to evidence to yield a posterior distribution
    evidence_noise = rng.normal(loc=0.0, scale=0.25, size=n_samples)
    evidence_samples = evidence + evidence_noise

    # Map evidence to probability via logistic transform
    prior_mean = alpha_prior / (alpha_prior + beta_prior)
    base_log_odds = np.log(prior_mean / (1 - prior_mean))

    log_odds = base_log_odds + evidence_samples
    prob_samples = 1 / (1 + np.exp(-log_odds))

    summary = {
        "mean": float(np.mean(prob_samples)),
        "p05": float(np.percentile(prob_samples, 5)),
        "p95": float(np.percentile(prob_samples, 95)),
    }
    return prob_samples, summary
