import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { ArrowLeft, Heart, MapPin, Calendar, Palette, Globe, User, Shield, Users } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const POS_ORDER = ["Goalkeeper", "Defence", "Midfield", "Offence"];

function getAge(dob) {
  if (!dob) return null;
  const diff = Date.now() - new Date(dob).getTime();
  return Math.floor(diff / (365.25 * 24 * 60 * 60 * 1000));
}

export default function TeamPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useLanguage();
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    fetchTeam();
  }, [id]);

  const fetchTeam = async () => {
    setLoading(true);
    try {
      const [teamRes, favsRes] = await Promise.allSettled([
        axios.get(`${API}/teams/${id}`),
        user ? axios.get(`${API}/favorites`, { withCredentials: true }) : Promise.resolve({ data: [] }),
      ]);
      if (teamRes.status === "fulfilled") setTeam(teamRes.value.data);
      if (favsRes.status === "fulfilled") {
        setIsFavorite(favsRes.value.data.some((f) => f.type === "team" && f.item_id === String(id)));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async () => {
    if (!user) { toast.info(t("nav.login") + "!"); navigate("/login"); return; }
    if (!team) return;
    try {
      const { data } = await axios.post(`${API}/favorites`,
        { type: "team", item_id: String(id), name: team.shortName || team.name, crest: team.crest || "" },
        { withCredentials: true });
      setIsFavorite(data.action === "added");
      toast.success(data.action === "added" ? "+" : "-");
    } catch { toast.error("Error"); }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 pt-6 space-y-4">
        <Skeleton className="h-14 w-48 rounded-2xl" />
        <Skeleton className="h-48 rounded-3xl" />
        <Skeleton className="h-32 rounded-3xl" />
        <Skeleton className="h-64 rounded-3xl" />
      </div>
    );
  }

  if (!team) {
    return (
      <div className="max-w-5xl mx-auto px-4 pt-6">
        <div className="card-tactile p-8 text-center">
          <p className="text-slate-500 font-semibold">{t("team.notFound")}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 pt-6 pb-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 animate-slide-up">
        <button data-testid="team-back-button" onClick={() => navigate(-1)}
          className="w-12 h-12 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center hover:bg-slate-50 transition-colors">
          <ArrowLeft size={20} strokeWidth={2.5} />
        </button>
        <div className="flex-1" />
        <button data-testid="team-favorite-toggle" onClick={toggleFavorite}
          className="w-12 h-12 rounded-full border-2 border-slate-300 flex items-center justify-center transition-all duration-200"
          style={isFavorite ? { backgroundColor: "#FEF3C7", borderColor: "#F59E0B" } : {}}>
          <Heart size={22} strokeWidth={2.5} className={isFavorite ? "text-yellow-500 fill-yellow-500" : "text-slate-400"} />
        </button>
      </div>

      {/* Team Hero */}
      <div className="card-tactile p-6 mb-6 animate-slide-up" style={{ animationDelay: "0.05s" }}>
        <div className="flex items-center gap-5">
          {team.crest && <img src={team.crest} alt={team.name} className="w-24 h-24 object-contain flex-shrink-0" />}
          <div className="min-w-0">
            <h1 className="text-2xl sm:text-3xl font-black text-slate-800 tracking-tight">{team.name}</h1>
            {team.venue && (
              <div className="flex items-center gap-1.5 mt-1.5 text-slate-500">
                <MapPin size={14} strokeWidth={2.5} />
                <span className="font-semibold text-sm">{team.venue}</span>
              </div>
            )}
            {/* Competitions */}
            {team.runningCompetitions?.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {team.runningCompetitions.map((c, i) => (
                  <span key={i} className="inline-flex items-center gap-1.5 bg-slate-100 rounded-full px-3 py-1 text-xs font-bold text-slate-600">
                    {c.emblem && <img src={c.emblem} alt="" className="w-3.5 h-3.5 object-contain" />}
                    {c.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 animate-slide-up" style={{ animationDelay: "0.1s" }}>
        {team.founded && (
          <div className="card-tactile p-4 text-center">
            <Calendar size={20} strokeWidth={2.5} className="text-sky-500 mx-auto mb-2" />
            <div className="text-xs font-bold uppercase tracking-widest text-slate-400">{t("team.founded")}</div>
            <div className="text-xl font-black text-slate-800 mt-1">{team.founded}</div>
          </div>
        )}
        {team.clubColors && (
          <div className="card-tactile p-4 text-center">
            <Palette size={20} strokeWidth={2.5} className="text-orange-500 mx-auto mb-2" />
            <div className="text-xs font-bold uppercase tracking-widest text-slate-400">{t("team.colors")}</div>
            <div className="text-sm font-bold text-slate-800 mt-1">{team.clubColors}</div>
          </div>
        )}
        {team.coach && (
          <div className="card-tactile p-4 text-center">
            <User size={20} strokeWidth={2.5} className="text-green-500 mx-auto mb-2" />
            <div className="text-xs font-bold uppercase tracking-widest text-slate-400">{t("team.coach")}</div>
            <div className="text-sm font-bold text-slate-800 mt-1">{team.coach.name}</div>
            {team.coach.nationality && (
              <div className="text-xs text-slate-400 font-semibold">{team.coach.nationality}</div>
            )}
          </div>
        )}
        <div className="card-tactile p-4 text-center">
          <Users size={20} strokeWidth={2.5} className="text-purple-500 mx-auto mb-2" />
          <div className="text-xs font-bold uppercase tracking-widest text-slate-400">{t("team.squad")}</div>
          <div className="text-xl font-black text-slate-800 mt-1">{team.squadCount}</div>
          <div className="text-xs text-slate-400 font-semibold">{t("team.players")}</div>
        </div>
      </div>

      {/* Squad */}
      <div className="animate-slide-up" style={{ animationDelay: "0.15s" }}>
        <div className="flex items-center gap-2 mb-4">
          <Shield size={22} strokeWidth={2.5} className="text-sky-500" />
          <h2 className="text-xl sm:text-2xl font-bold text-slate-800">{t("team.squad")}</h2>
        </div>

        {POS_ORDER.map((pos) => {
          const players = team.squad?.[pos];
          if (!players || players.length === 0) return null;
          return (
            <div key={pos} className="mb-5">
              <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-2 pl-1">
                {t(`team.pos.${pos.toLowerCase()}`)}
              </h3>
              <div className="card-tactile overflow-hidden">
                {players.map((p, i) => (
                  <div
                    key={p.id || i}
                    data-testid={`player-${p.id}`}
                    className={`flex items-center gap-3 px-4 py-3 ${i % 2 === 0 ? "bg-slate-50/50" : ""} ${i < players.length - 1 ? "border-b border-slate-100" : ""}`}
                  >
                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-black text-slate-500">{i + 1}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-bold text-slate-800 text-sm truncate">{p.name}</div>
                      <div className="text-xs text-slate-400 font-semibold">
                        {p.nationality}
                        {p.dateOfBirth && ` · ${getAge(p.dateOfBirth)} ${t("team.yrs")}`}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
