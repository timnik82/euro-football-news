import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import MatchCard from "@/components/MatchCard";
import MatchDetailModal from "@/components/MatchDetailModal";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { ArrowLeft, Heart, Star, ChevronRight } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const LEAGUE_COLORS = {
  PL: "#7C3AED", CL: "#1E3A5F", PD: "#F97316",
  SA: "#059669", BL1: "#DC2626", FL1: "#1D4ED8", PPL: "#15803D",
};

export function LeaguesList() {
  const [leagues, setLeagues] = useState([]);
  const navigate = useNavigate();
  const { t } = useLanguage();

  useEffect(() => {
    axios.get(`${API}/leagues`).then((r) => setLeagues(r.data)).catch(console.error);
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 pt-6">
      <h1 className="text-4xl sm:text-5xl font-black text-slate-800 tracking-tight mb-6 animate-slide-up">
        {t("nav.leagues")}
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
        {leagues.map((league, i) => (
          <button
            key={league.code}
            data-testid={`leagues-list-card-${league.code}`}
            onClick={() => navigate(`/league/${league.code}`)}
            className="card-tactile p-6 text-left flex items-center gap-5 min-h-[100px] animate-slide-up"
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            {league.emblem ? (
              <img src={league.emblem} alt={league.name} className="w-16 h-16 object-contain flex-shrink-0" />
            ) : (
              <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                <ChevronRight size={24} strokeWidth={2.5} className="text-slate-400" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="text-lg font-black text-slate-800">{league.name}</div>
              <div className="text-sm font-semibold text-slate-400 mt-0.5">{league.country}</div>
            </div>
            <ChevronRight size={22} strokeWidth={2.5} className="text-slate-300 flex-shrink-0" />
          </button>
        ))}
      </div>
    </div>
  );
}

export default function LeagueDetail() {
  const { code } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useLanguage();
  const [standings, setStandings] = useState([]);
  const [recentMatches, setRecentMatches] = useState([]);
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [scorers, setScorers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [selectedMatchId, setSelectedMatchId] = useState(null);

  const leagueName = {
    PL: "Premier League", CL: "Champions League", PD: "La Liga",
    SA: "Serie A", BL1: "Bundesliga", FL1: "Ligue 1", PPL: "Primeira Liga",
  }[code] || code;

  const leagueEmblem = {
    PL: "https://crests.football-data.org/PL.png",
    CL: "https://crests.football-data.org/CL.png",
    PD: "https://crests.football-data.org/laliga.png",
    SA: "https://crests.football-data.org/c111.png",
    BL1: "https://crests.football-data.org/BL1.png",
    FL1: "https://crests.football-data.org/FL1.png",
    PPL: "https://crests.football-data.org/PPL.png",
  }[code] || "";

  const color = LEAGUE_COLORS[code] || "#0EA5E9";

  useEffect(() => {
    fetchAll();
  }, [code]);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [standingsRes, recentRes, upcomingRes, scorersRes, favsRes] = await Promise.allSettled([
        axios.get(`${API}/leagues/${code}/standings`),
        axios.get(`${API}/leagues/${code}/matches?status=FINISHED&limit=10`),
        axios.get(`${API}/leagues/${code}/matches?status=SCHEDULED&limit=10`),
        axios.get(`${API}/leagues/${code}/scorers`),
        user ? axios.get(`${API}/favorites`, { withCredentials: true }) : Promise.resolve({ data: [] }),
      ]);
      if (standingsRes.status === "fulfilled") setStandings(standingsRes.value.data);
      if (recentRes.status === "fulfilled") setRecentMatches(recentRes.value.data);
      if (upcomingRes.status === "fulfilled") setUpcomingMatches(upcomingRes.value.data);
      if (scorersRes.status === "fulfilled") setScorers(scorersRes.value.data);
      if (favsRes.status === "fulfilled") {
        const favs = favsRes.value.data;
        setFavorites(favs);
        setIsFavorite(favs.some((f) => f.type === "league" && f.item_id === code));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async () => {
    if (!user) { toast.info(t("nav.login") + "!"); navigate("/login"); return; }
    try {
      const { data } = await axios.post(
        `${API}/favorites`,
        { type: "league", item_id: code, name: leagueName, crest: "" },
        { withCredentials: true }
      );
      setIsFavorite(data.action === "added");
      toast.success(data.action === "added" ? "+" : "-");
    } catch { toast.error("Error"); }
  };

  const isTeamFavorite = (teamId) => favorites.some((f) => f.type === "team" && f.item_id === String(teamId));

  const toggleTeamFavorite = async (team) => {
    if (!user) { toast.info(t("nav.login") + "!"); navigate("/login"); return; }
    try {
      const { data } = await axios.post(
        `${API}/favorites`,
        { type: "team", item_id: String(team.id), name: team.shortName || team.name, crest: team.crest || "", league_code: code },
        { withCredentials: true }
      );
      if (data.action === "added") {
        setFavorites([...favorites, { type: "team", item_id: String(team.id) }]);
        toast.success(`${team.shortName || team.name} +`);
      } else {
        setFavorites(favorites.filter((f) => !(f.type === "team" && f.item_id === String(team.id))));
        toast.success("-");
      }
    } catch { toast.error("Error"); }
  };

  const allStandingsTable = standings.flatMap((s) => s.table || []);

  return (
    <div className="max-w-5xl mx-auto px-4 pt-6">
      <div className="flex items-center gap-3 mb-6 animate-slide-up">
        <button data-testid="league-back-button" onClick={() => navigate(-1)}
          className="w-12 h-12 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center hover:bg-slate-50 transition-colors">
          <ArrowLeft size={20} strokeWidth={2.5} />
        </button>
        {leagueEmblem && (
          <img src={leagueEmblem} alt={leagueName} className="w-12 h-12 object-contain" />
        )}
        <div className="flex-1">
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-slate-800">{leagueName}</h1>
        </div>
        <button data-testid="league-favorite-toggle" onClick={toggleFavorite}
          className="w-12 h-12 rounded-full border-2 border-slate-300 flex items-center justify-center transition-all duration-200"
          style={isFavorite ? { backgroundColor: "#FEF3C7", borderColor: "#F59E0B" } : {}}>
          <Heart size={22} strokeWidth={2.5} className={isFavorite ? "text-yellow-500 fill-yellow-500" : "text-slate-400"} />
        </button>
      </div>

      {loading ? (
        <div className="space-y-4">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 rounded-3xl" />)}</div>
      ) : (
        <Tabs defaultValue="standings" className="animate-slide-up" style={{ animationDelay: "0.05s" }}>
          <TabsList className="w-full rounded-2xl bg-white border-2 border-slate-200 p-1.5 h-auto mb-6">
            <TabsTrigger data-testid="tab-standings" value="standings"
              className="flex-1 rounded-xl font-bold text-sm data-[state=active]:bg-sky-500 data-[state=active]:text-white py-3 min-h-[48px]">
              {t("league.table")}
            </TabsTrigger>
            <TabsTrigger data-testid="tab-matches" value="matches"
              className="flex-1 rounded-xl font-bold text-sm data-[state=active]:bg-sky-500 data-[state=active]:text-white py-3 min-h-[48px]">
              {t("league.matches")}
            </TabsTrigger>
            <TabsTrigger data-testid="tab-scorers" value="scorers"
              className="flex-1 rounded-xl font-bold text-sm data-[state=active]:bg-sky-500 data-[state=active]:text-white py-3 min-h-[48px]">
              {t("league.topScorers")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="standings">
            {allStandingsTable.length === 0 ? (
              <div className="card-tactile p-8 text-center"><p className="text-slate-500 font-semibold">{t("league.noStandings")}</p></div>
            ) : (
              <div className="card-tactile overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b-2 border-slate-200">
                        <th className="text-left p-3 font-bold text-slate-500 w-8">#</th>
                        <th className="text-left p-3 font-bold text-slate-500">{t("league.team")}</th>
                        <th className="text-center p-3 font-bold text-slate-500 w-10">{t("league.played")}</th>
                        <th className="text-center p-3 font-bold text-slate-500 w-10">{t("league.won")}</th>
                        <th className="text-center p-3 font-bold text-slate-500 w-10">{t("league.drawn")}</th>
                        <th className="text-center p-3 font-bold text-slate-500 w-10">{t("league.lost")}</th>
                        <th className="text-center p-3 font-bold text-slate-500 w-12">{t("league.gd")}</th>
                        <th className="text-center p-3 font-bold text-slate-800 w-12">{t("league.points")}</th>
                        <th className="w-10 p-3"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {allStandingsTable.map((row, i) => (
                        <tr key={row.team?.id || i}
                          className={`border-b border-slate-100 transition-colors hover:bg-sky-50 ${i % 2 === 0 ? "bg-slate-50/50" : ""}`}>
                          <td className="p-3 font-black text-slate-400">{row.position}</td>
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              {row.team?.crest && <img src={row.team.crest} alt="" className="w-6 h-6 object-contain flex-shrink-0" />}
                              <span className="font-bold text-slate-800 truncate">{row.team?.shortName || row.team?.name}</span>
                            </div>
                          </td>
                          <td className="text-center p-3 font-semibold text-slate-600">{row.playedGames}</td>
                          <td className="text-center p-3 font-semibold text-green-600">{row.won}</td>
                          <td className="text-center p-3 font-semibold text-slate-500">{row.draw}</td>
                          <td className="text-center p-3 font-semibold text-red-500">{row.lost}</td>
                          <td className="text-center p-3 font-bold text-slate-700">{row.goalDifference > 0 ? `+${row.goalDifference}` : row.goalDifference}</td>
                          <td className="text-center p-3 font-black text-lg" style={{ color }}>{row.points}</td>
                          <td className="p-3">
                            <button data-testid={`fav-team-${row.team?.id}`} onClick={() => toggleTeamFavorite(row.team)}
                              className="p-1 rounded-full hover:bg-yellow-50 transition-colors">
                              <Heart size={16} strokeWidth={2.5}
                                className={isTeamFavorite(row.team?.id) ? "text-yellow-500 fill-yellow-500" : "text-slate-300"} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="matches">
            {upcomingMatches.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
                  <Star size={20} strokeWidth={2.5} className="text-sky-500" /> {t("league.upcoming")}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {upcomingMatches.map((m, i) => <MatchCard key={m.id || i} match={m} onClick={setSelectedMatchId} />)}
                </div>
              </div>
            )}
            {recentMatches.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-slate-800 mb-3">{t("league.recentResults")}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {recentMatches.map((m, i) => <MatchCard key={m.id || i} match={m} onClick={setSelectedMatchId} />)}
                </div>
              </div>
            )}
            {upcomingMatches.length === 0 && recentMatches.length === 0 && (
              <div className="card-tactile p-8 text-center"><p className="text-slate-500 font-semibold">{t("league.noMatches")}</p></div>
            )}
          </TabsContent>

          <TabsContent value="scorers">
            {scorers.length === 0 ? (
              <div className="card-tactile p-8 text-center"><p className="text-slate-500 font-semibold">{t("league.noScorers")}</p></div>
            ) : (
              <div className="card-tactile overflow-hidden">
                <div className="p-4 border-b-2 border-slate-200 flex items-center gap-3">
                  <img src="https://images.unsplash.com/photo-1518091043644-c1d4457512c6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNTl8MHwxfHNlYXJjaHwxfHxmb290YmFsbCUyMHRyb3BoeXxlbnwwfHx8fDE3NzU1OTY2MTd8MA&ixlib=rb-4.1.0&q=85"
                    alt="" className="w-10 h-10 rounded-xl object-cover" />
                  <h3 className="text-lg font-black text-slate-800">{t("league.topScorers")}</h3>
                </div>
                <div>
                  {scorers.map((scorer, i) => (
                    <div key={scorer.player?.id || i}
                      className={`flex items-center gap-3 p-4 border-b border-slate-100 ${i % 2 === 0 ? "bg-slate-50/50" : ""}`}>
                      <span className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-sm ${
                        i === 0 ? "bg-yellow-400 text-white" : i === 1 ? "bg-slate-300 text-white" : i === 2 ? "bg-amber-600 text-white" : "bg-slate-100 text-slate-500"
                      }`}>{i + 1}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-slate-800 truncate">{scorer.player?.name}</div>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          {scorer.team?.crest && <img src={scorer.team.crest} alt="" className="w-4 h-4 object-contain" />}
                          <span className="text-xs font-semibold text-slate-500 truncate">{scorer.team?.shortName || scorer.team?.name}</span>
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="text-xl font-black" style={{ color }}>{scorer.goals}</div>
                        <div className="text-xs font-bold text-slate-400">{scorer.assists || 0} {t("league.ast")}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
      <MatchDetailModal
        matchId={selectedMatchId}
        open={!!selectedMatchId}
        onClose={() => setSelectedMatchId(null)}
      />
    </div>
  );
}
