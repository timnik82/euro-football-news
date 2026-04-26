// Single source of truth for league metadata on the frontend.
// Backend authoritative copy lives in /app/backend/server.py (LEAGUES, LEAGUE_COLORS).
export const LEAGUES = {
  PL: { name: "Premier League", country: "England", color: "#7C3AED", emblem: "https://crests.football-data.org/PL.png" },
  CL: { name: "Champions League", country: "Europe", color: "#1E3A5F", emblem: "https://crests.football-data.org/CL.png" },
  PD: { name: "La Liga", country: "Spain", color: "#F97316", emblem: "https://crests.football-data.org/laliga.png" },
  SA: { name: "Serie A", country: "Italy", color: "#059669", emblem: "https://crests.football-data.org/c111.png" },
  BL1: { name: "Bundesliga", country: "Germany", color: "#DC2626", emblem: "https://crests.football-data.org/BL1.png" },
  FL1: { name: "Ligue 1", country: "France", color: "#1D4ED8", emblem: "https://crests.football-data.org/FL1.png" },
  PPL: { name: "Primeira Liga", country: "Portugal", color: "#15803D", emblem: "https://crests.football-data.org/PPL.png" },
};

export const DEFAULT_LEAGUE_COLOR = "#0EA5E9";

export function getLeague(code) {
  return LEAGUES[code] || { name: code, country: "", color: DEFAULT_LEAGUE_COLOR, emblem: "" };
}
