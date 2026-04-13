import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { MapPin, Calendar, Hash, Flag, Briefcase, Shield } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function getAge(dob) {
  if (!dob) return null;
  return Math.floor((Date.now() - new Date(dob).getTime()) / (365.25 * 24 * 60 * 60 * 1000));
}

const POS_LABELS = {
  en: {
    Goalkeeper: "Goalkeeper", "Centre-Back": "Centre-Back", "Right-Back": "Right-Back", "Left-Back": "Left-Back",
    Defence: "Defender", "Defensive Midfield": "Defensive Midfielder", "Central Midfield": "Central Midfielder",
    "Attacking Midfield": "Attacking Midfielder", Midfield: "Midfielder", "Right Winger": "Right Winger",
    "Left Winger": "Left Winger", "Centre-Forward": "Centre-Forward", Offence: "Forward",
  },
  ru: {
    Goalkeeper: "Вратарь", "Centre-Back": "Центральный защитник", "Right-Back": "Правый защитник", "Left-Back": "Левый защитник",
    Defence: "Защитник", "Defensive Midfield": "Опорный полузащитник", "Central Midfield": "Центральный полузащитник",
    "Attacking Midfield": "Атакующий полузащитник", Midfield: "Полузащитник", "Right Winger": "Правый вингер",
    "Left Winger": "Левый вингер", "Centre-Forward": "Центральный нападающий", Offence: "Нападающий",
  },
  pt: {
    Goalkeeper: "Guarda-redes", "Centre-Back": "Defesa central", "Right-Back": "Lateral direito", "Left-Back": "Lateral esquerdo",
    Defence: "Defesa", "Defensive Midfield": "Medio defensivo", "Central Midfield": "Medio centro",
    "Attacking Midfield": "Medio ofensivo", Midfield: "Medio", "Right Winger": "Extremo direito",
    "Left Winger": "Extremo esquerdo", "Centre-Forward": "Ponta de lanca", Offence: "Avancado",
  },
};

const POS_COLORS = {
  Goalkeeper: { bg: "bg-amber-100", text: "text-amber-700", border: "border-amber-300" },
  Defence: { bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-300" },
  Midfield: { bg: "bg-green-100", text: "text-green-700", border: "border-green-300" },
  Offence: { bg: "bg-red-100", text: "text-red-700", border: "border-red-300" },
};

function getSectionColor(pos) {
  if (!pos) return POS_COLORS.Midfield;
  if (pos === "Goalkeeper") return POS_COLORS.Goalkeeper;
  if (pos.includes("Back") || pos === "Defence" || pos === "Centre-Back") return POS_COLORS.Defence;
  if (pos.includes("Midfield") || pos === "Midfield") return POS_COLORS.Midfield;
  return POS_COLORS.Offence;
}

export default function PlayerDetailModal({ playerId, open, onClose }) {
  const { t, language } = useLanguage();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (open && playerId) {
      setLoading(true);
      setData(null);
      axios
        .get(`${API}/players/${playerId}`)
        .then((r) => setData(r.data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [open, playerId]);

  if (!open) return null;
  const p = data;
  const posLabel = p?.position ? (POS_LABELS[language]?.[p.position] || p.position) : null;
  const sectionLabel = p?.section ? (POS_LABELS[language]?.[p.section] || p.section) : null;
  const displayPos = posLabel || sectionLabel;
  const posColor = getSectionColor(p?.position || p?.section);
  const age = getAge(p?.dateOfBirth);

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) onClose(); }}>
      <DialogContent className="max-w-sm w-[90vw] rounded-3xl border-2 border-slate-200 p-0 overflow-hidden bg-white" data-testid="player-detail-modal">
        {loading ? (
          <div className="p-8 space-y-4">
            <Skeleton className="h-20 rounded-2xl" />
            <Skeleton className="h-10 rounded-2xl" />
            <Skeleton className="h-32 rounded-2xl" />
          </div>
        ) : !p ? (
          <div className="p-8 text-center text-slate-500 font-semibold">{t("player.notFound")}</div>
        ) : (
          <>
            {/* Header */}
            <div className={`px-6 pt-6 pb-5 ${posColor.bg} border-b-2 ${posColor.border}`}>
              <div className="flex items-center gap-4">
                {/* Shirt number circle */}
                <div className={`w-16 h-16 rounded-full bg-white border-3 ${posColor.border} flex items-center justify-center flex-shrink-0 shadow-sm`}>
                  {p.shirtNumber ? (
                    <span className={`text-2xl font-black ${posColor.text}`}>{p.shirtNumber}</span>
                  ) : (
                    <Shield size={24} strokeWidth={2.5} className={posColor.text} />
                  )}
                </div>
                <div className="min-w-0">
                  <h2 className="text-xl font-black text-slate-800 leading-tight">{p.name}</h2>
                  {displayPos && (
                    <span className={`inline-block mt-1.5 px-3 py-1 rounded-full text-xs font-bold ${posColor.bg} ${posColor.text} border ${posColor.border}`}>
                      {displayPos}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Info */}
            <div className="px-6 py-5 space-y-4">
              {/* Team */}
              {p.currentTeam && (
                <button
                  data-testid="player-team-link"
                  onClick={() => { onClose(); navigate(`/team/${p.currentTeam.id}`); }}
                  className="flex items-center gap-3 w-full text-left hover:bg-slate-50 rounded-2xl p-2 -mx-2 transition-colors"
                >
                  {p.currentTeam.crest && (
                    <img src={p.currentTeam.crest} alt="" className="w-10 h-10 object-contain flex-shrink-0" />
                  )}
                  <div>
                    <div className="text-xs font-bold uppercase tracking-widest text-slate-400">{t("player.club")}</div>
                    <div className="font-bold text-slate-800">{p.currentTeam.name}</div>
                  </div>
                </button>
              )}

              {/* Details grid */}
              <div className="grid grid-cols-2 gap-3">
                {p.nationality && (
                  <div className="flex items-center gap-2.5">
                    <Flag size={16} strokeWidth={2.5} className="text-slate-400 flex-shrink-0" />
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{t("player.nationality")}</div>
                      <div className="text-sm font-bold text-slate-800">{p.nationality}</div>
                    </div>
                  </div>
                )}

                {age && (
                  <div className="flex items-center gap-2.5">
                    <Calendar size={16} strokeWidth={2.5} className="text-slate-400 flex-shrink-0" />
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{t("player.age")}</div>
                      <div className="text-sm font-bold text-slate-800">{age} {t("team.yrs")}</div>
                    </div>
                  </div>
                )}

                {p.dateOfBirth && (
                  <div className="flex items-center gap-2.5">
                    <Calendar size={16} strokeWidth={2.5} className="text-slate-400 flex-shrink-0" />
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{t("player.born")}</div>
                      <div className="text-sm font-bold text-slate-800">
                        {new Date(p.dateOfBirth).toLocaleDateString(language === "ru" ? "ru-RU" : language === "pt" ? "pt-PT" : "en-GB", { day: "numeric", month: "short", year: "numeric" })}
                      </div>
                    </div>
                  </div>
                )}

                {p.shirtNumber && (
                  <div className="flex items-center gap-2.5">
                    <Hash size={16} strokeWidth={2.5} className="text-slate-400 flex-shrink-0" />
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{t("player.number")}</div>
                      <div className="text-sm font-bold text-slate-800">#{p.shirtNumber}</div>
                    </div>
                  </div>
                )}

                {p.contract && (
                  <div className="flex items-center gap-2.5 col-span-2">
                    <Briefcase size={16} strokeWidth={2.5} className="text-slate-400 flex-shrink-0" />
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{t("player.contract")}</div>
                      <div className="text-sm font-bold text-slate-800">
                        {p.contract.start} &rarr; {p.contract.until}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
