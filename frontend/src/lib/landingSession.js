const SKIP_LANDING_KEY = "gk_skip_landing";

export function hasSkippedLanding() {
  try {
    return sessionStorage.getItem(SKIP_LANDING_KEY) === "1";
  } catch {
    return false;
  }
}

export function skipLanding() {
  try {
    sessionStorage.setItem(SKIP_LANDING_KEY, "1");
  } catch {
    // Storage may be blocked (e.g. private browsing); the landing page
    // will just show again next time, which is an acceptable fallback.
  }
}
