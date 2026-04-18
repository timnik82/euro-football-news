import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useLanguage } from "@/contexts/LanguageContext";
import { Search, X, Users, User } from "lucide-react";
import PlayerDetailModal from "@/components/PlayerDetailModal";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function SearchModal({ open, onClose }) {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState({ teams: [], players: [] });
  const [loading, setLoading] = useState(false);
  const [selectedPlayerId, setSelectedPlayerId] = useState(null);

  const debouncedQuery = useDebounce(query, 350);

  useEffect(() => {
    if (open) {
      setQuery("");
      setResults({ teams: [], players: [] });
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  const fetchResults = useCallback(async (q) => {
    if (!q || q.length < 2) {
      setResults({ teams: [], players: [] });
      return;
    }
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/search?q=${encodeURIComponent(q)}`);
      setResults(data);
    } catch {
      setResults({ teams: [], players: [] });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResults(debouncedQuery);
  }, [debouncedQuery, fetchResults]);

  const handleTeamClick = (team) => {
    onClose();
    navigate(`/team/${team.id}`);
  };

  const handlePlayerClick = (player) => {
    setSelectedPlayerId(player.id);
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  const hasResults = results.teams.length > 0 || results.players.length > 0;
  const showHint = query.length > 0 && query.length < 2;
  const showNoResults = debouncedQuery.length >= 2 && !loading && !hasResults;

  if (!open) return null;

  return (
    <>
      {/* Full-screen backdrop */}
      <div
        data-testid="search-modal-backdrop"
        className="fixed inset-0 z-[200] bg-slate-900/60 backdrop-blur-sm flex flex-col items-stretch pt-4 px-3 pb-6 animate-fade-in"
        onClick={handleBackdropClick}
        style={{ animation: "fadeIn 0.15s ease" }}
      >
        {/* Search box */}
        <div className="max-w-lg w-full mx-auto">
          {/* Input bar */}
          <div className="flex items-center gap-3 bg-white rounded-2xl px-4 py-3 shadow-xl border-2 border-sky-200">
            <Search size={20} strokeWidth={2.5} className="text-sky-400 flex-shrink-0" />
            <input
              ref={inputRef}
              data-testid="search-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("search.placeholder")}
              className="flex-1 bg-transparent text-slate-800 font-semibold text-base outline-none placeholder:text-slate-400"
            />
            {query.length > 0 ? (
              <button
                data-testid="search-clear-btn"
                onClick={() => setQuery("")}
                className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center hover:bg-slate-200 transition-colors flex-shrink-0"
              >
                <X size={14} strokeWidth={3} className="text-slate-500" />
              </button>
            ) : (
              <button
                data-testid="search-close-btn"
                onClick={onClose}
                className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center hover:bg-slate-200 transition-colors flex-shrink-0"
              >
                <X size={14} strokeWidth={3} className="text-slate-500" />
              </button>
            )}
          </div>

          {/* Results panel */}
          {(query.length >= 2 || loading) && (
            <div
              data-testid="search-results-panel"
              className="mt-3 bg-white rounded-2xl shadow-xl border-2 border-slate-200 overflow-hidden max-h-[70vh] overflow-y-auto"
            >
              {loading && (
                <div className="p-6 flex justify-center">
                  <div className="w-6 h-6 border-3 border-sky-400 border-t-transparent rounded-full animate-spin" />
                </div>
              )}

              {!loading && showNoResults && (
                <div className="p-8 text-center text-slate-400 font-semibold text-sm" data-testid="search-no-results">
                  {t("search.noResults")}
                </div>
              )}

              {!loading && results.teams.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 px-4 pt-4 pb-2">
                    <Users size={14} strokeWidth={2.5} className="text-sky-500" />
                    <span className="text-xs font-black text-slate-500 uppercase tracking-widest">
                      {t("search.teams")}
                    </span>
                  </div>
                  {results.teams.map((team) => (
                    <button
                      key={team.id}
                      data-testid={`search-team-${team.id}`}
                      onClick={() => handleTeamClick(team)}
                      className="w-full flex items-center gap-3 px-4 py-3 hover:bg-sky-50 transition-colors text-left border-b border-slate-100 last:border-0"
                    >
                      {team.crest ? (
                        <img src={team.crest} alt="" className="w-9 h-9 object-contain flex-shrink-0" />
                      ) : (
                        <div className="w-9 h-9 rounded-full bg-slate-100 flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-slate-800 truncate">{team.name}</div>
                        <div className="text-xs font-semibold text-slate-400 truncate">{team.league}</div>
                      </div>
                      <span className="text-xs font-bold text-sky-400 flex-shrink-0">›</span>
                    </button>
                  ))}
                </div>
              )}

              {!loading && results.players.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 px-4 pt-4 pb-2">
                    <User size={14} strokeWidth={2.5} className="text-orange-500" />
                    <span className="text-xs font-black text-slate-500 uppercase tracking-widest">
                      {t("search.players")}
                    </span>
                  </div>
                  {results.players.map((player) => (
                    <button
                      key={player.id}
                      data-testid={`search-player-${player.id}`}
                      onClick={() => handlePlayerClick(player)}
                      className="w-full flex items-center gap-3 px-4 py-3 hover:bg-orange-50 transition-colors text-left border-b border-slate-100 last:border-0"
                    >
                      {player.teamCrest ? (
                        <img src={player.teamCrest} alt="" className="w-9 h-9 object-contain flex-shrink-0" />
                      ) : (
                        <div className="w-9 h-9 rounded-full bg-slate-100 flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-slate-800 truncate">{player.name}</div>
                        <div className="text-xs font-semibold text-slate-400 truncate">
                          {player.team} · {player.league}
                        </div>
                      </div>
                      <div className="flex-shrink-0 text-right">
                        <div className="text-base font-black text-orange-500">{player.goals}</div>
                        <div className="text-[10px] font-bold text-slate-400">goals</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Hint when typing < 2 chars */}
          {showHint && (
            <div className="mt-3 text-center text-slate-300 text-sm font-semibold">
              {t("search.hint")}
            </div>
          )}
        </div>
      </div>

      {/* Player detail modal */}
      <PlayerDetailModal
        playerId={selectedPlayerId}
        open={!!selectedPlayerId}
        onClose={() => setSelectedPlayerId(null)}
      />
    </>
  );
}
