import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { localizeStory } from "@/i18n/translations";
import axios from "axios";
import MatchCard from "@/components/MatchCard";
import MatchDetailModal from "@/components/MatchDetailModal";
import SettingsGear from "@/components/SettingsGear";
import { Skeleton } from "@/components/ui/skeleton";
import { Trophy, Zap, Newspaper, ChevronRight, Calendar } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function HomePage() {
  const { user } = useAuth();
  const { t, language, dateLocale } = useLanguage();
  const navigate = useNavigate();
  const [leagues, setLeagues] = useState([]);
  const [todayMatches, setTodayMatches] = useState([]);
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatchId, setSelectedMatchId] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [leaguesRes, todayRes, upcomingRes, storiesRes] = await Promise.allSettled([
        axios.get(`${API}/leagues`),
        axios.get(`${API}/matches/today`),
        axios.get(`${API}/matches/upcoming`),
        axios.get(`${API}/stories`),
      ]);
      if (leaguesRes.status === "fulfilled") setLeagues(leaguesRes.value.data);
      if (todayRes.status === "fulfilled") setTodayMatches(todayRes.value.data);
      if (upcomingRes.status === "fulfilled") setUpcomingMatches(upcomingRes.value.data);
      if (storiesRes.status === "fulfilled") setStories(storiesRes.value.data);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  };

  const hasMatchesToday = todayMatches.length > 0;
  const displayMatches = hasMatchesToday ? todayMatches : upcomingMatches.slice(0, 6);
  const localizedStories = stories.map((s) => localizeStory(s, language));

  const formattedDate = new Date().toLocaleDateString(dateLocale, {
    weekday: "long", month: "long", day: "numeric",
  });

  return (
    <div className="max-w-5xl mx-auto px-4 pt-6 pb-4">
      {/* Welcome header */}
      <div className="mb-6 animate-slide-up flex items-start justify-between">
        <div>
          <h1 className="text-4xl sm:text-5xl font-black text-slate-800 tracking-tight">
            {user ? `${t("home.title").replace("!", "")} ${user.name}!` : t("home.title")}
          </h1>
          <p className="text-base sm:text-lg font-semibold text-slate-500 mt-1 capitalize">
            {formattedDate}
          </p>
        </div>
        <SettingsGear />
      </div>

      {/* League selector pills */}
      <div className="mb-8 animate-slide-up" style={{ animationDelay: "0.05s" }}>
        <div className="flex gap-3 overflow-x-auto scrollbar-hide pb-2">
          {leagues.map((league) => (
            <button
              key={league.code}
              data-testid={`league-pill-${league.code}`}
              onClick={() => navigate(`/league/${league.code}`)}
              className="whitespace-nowrap px-4 py-2.5 rounded-full text-sm font-bold border-2 border-slate-300 bg-white hover:bg-slate-50 hover:border-slate-400 transition-all duration-200 min-h-[48px] flex-shrink-0 flex items-center gap-2"
            >
              {league.emblem && <img src={league.emblem} alt="" className="w-5 h-5 object-contain" />}
              {league.name}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-36 rounded-3xl" />
          ))}
        </div>
      ) : (
        <>
          {/* Today's / Upcoming Matches */}
          <section className="mb-8 animate-slide-up" style={{ animationDelay: "0.1s" }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                {hasMatchesToday ? (
                  <Zap size={24} strokeWidth={2.5} className="text-yellow-500" />
                ) : (
                  <Calendar size={24} strokeWidth={2.5} className="text-sky-500" />
                )}
                <h2 className="text-2xl sm:text-3xl font-bold text-slate-800">
                  {hasMatchesToday ? t("home.todayMatches") : t("home.comingUp")}
                </h2>
              </div>
              {displayMatches.length > 0 && (
                <button
                  data-testid="see-all-matches-btn"
                  onClick={() => navigate("/leagues")}
                  className="flex items-center gap-1 text-sky-500 font-bold text-sm hover:text-sky-600 transition-colors"
                >
                  {t("home.seeAll")} <ChevronRight size={16} strokeWidth={3} />
                </button>
              )}
            </div>

            {displayMatches.length === 0 ? (
              <div className="card-tactile p-8 text-center">
                <Calendar size={48} strokeWidth={2} className="text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500 font-semibold text-lg">{t("home.noMatches")}</p>
                <p className="text-slate-400 font-medium text-sm mt-1">{t("home.noMatchesSub")}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {displayMatches.slice(0, 6).map((match, i) => (
                  <div key={match.id || i} className="animate-slide-up" style={{ animationDelay: `${0.1 + i * 0.05}s` }}>
                    <MatchCard match={match} onClick={setSelectedMatchId} />
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Match Stories */}
          {localizedStories.length > 0 && (
            <section className="mb-8 animate-slide-up" style={{ animationDelay: "0.2s" }}>
              <div className="flex items-center gap-2 mb-4">
                <Newspaper size={24} strokeWidth={2.5} className="text-orange-500" />
                <h2 className="text-2xl sm:text-3xl font-bold text-slate-800">{t("home.stories")}</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {localizedStories.slice(0, 6).map((story, i) => (
                  <div
                    key={story.match_id || i}
                    data-testid={`story-card-${i}`}
                    className="card-tactile p-5 cursor-pointer"
                    onClick={() => {
                      if (story.match_id) setSelectedMatchId(story.match_id);
                      else if (story.competition?.code) navigate(`/league/${story.competition.code}`);
                    }}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      {story.competition?.emblem && (
                        <img src={story.competition.emblem} alt="" className="w-5 h-5 object-contain" />
                      )}
                      <span className="text-xs font-bold uppercase tracking-widest text-slate-400">
                        {story.competition?.name}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-slate-800 mb-2 leading-snug">
                      {story.headline}
                    </h3>
                    <div className="flex items-center gap-3 mb-2">
                      <div className="flex items-center gap-2">
                        {story.home_team?.crest && <img src={story.home_team.crest} alt="" className="w-6 h-6 object-contain" />}
                        <span className="text-sm font-semibold">{story.home_team?.name}</span>
                      </div>
                      <span className="text-lg font-black text-sky-500">
                        {story.score?.home} - {story.score?.away}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{story.away_team?.name}</span>
                        {story.away_team?.crest && <img src={story.away_team.crest} alt="" className="w-6 h-6 object-contain" />}
                      </div>
                    </div>
                    <p className="text-sm text-slate-500 font-medium">{story.summary}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Quick League Cards */}
          <section className="animate-slide-up" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center gap-2 mb-4">
              <Trophy size={24} strokeWidth={2.5} className="text-yellow-500" />
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-800">{t("home.explore")}</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {leagues.map((league) => (
                <button
                  key={league.code}
                  data-testid={`league-card-${league.code}`}
                  onClick={() => navigate(`/league/${league.code}`)}
                  className="card-tactile p-5 text-left flex flex-col items-center gap-3 min-h-[130px] justify-center"
                >
                  {league.emblem ? (
                    <img src={league.emblem} alt={league.name} className="w-14 h-14 object-contain" />
                  ) : (
                    <Trophy size={32} strokeWidth={2} className="text-slate-300" />
                  )}
                  <div className="text-center">
                    <div className="text-sm font-black text-slate-800">{league.name}</div>
                    <div className="text-xs font-semibold text-slate-400 mt-0.5">{league.country}</div>
                  </div>
                </button>
              ))}
            </div>
          </section>
        </>
      )}
      <MatchDetailModal
        matchId={selectedMatchId}
        open={!!selectedMatchId}
        onClose={() => setSelectedMatchId(null)}
      />
    </div>
  );
}
