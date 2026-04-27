import { useState, useEffect } from "react";
import axios from "axios";
import { format, parseISO } from "date-fns";
import { useLanguage } from "@/contexts/LanguageContext";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Clock, MapPin, User, Swords, Calendar, Trophy, Zap } from "lucide-react";
import MatchStorySection from "@/components/MatchStorySection";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function MatchDetailModal({ matchId, open, onClose }) {
  const { t, dateLocale, language } = useLanguage();
  const [data, setData] = useState(null);
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [storyLoading, setStoryLoading] = useState(false);
  const [storyError, setStoryError] = useState(false);

  useEffect(() => {
    if (open && matchId) {
      setLoading(true);
      setData(null);
      setStory(null);
      setStoryError(false);
      setStoryLoading(true);
      axios
        .get(`${API}/matches/${matchId}`)
        .then((r) => setData(r.data))
        .catch(console.error)
        .finally(() => setLoading(false));
      axios
        .get(`${API}/matches/${matchId}/story`, { params: { lang: language } })
        .then((r) => setStory(r.data))
        .catch((err) => {
          console.error(err);
          setStoryError(true);
        })
        .finally(() => setStoryLoading(false));
    }
  }, [open, matchId, language]);

  if (!open) return null;

  const m = data;
  const isFinished = m?.status === "FINISHED";
  const isLive = m?.status === "IN_PLAY" || m?.status === "PAUSED";
  const score = m?.score || {};
  const ft = score.fullTime || {};
  const ht = score.halfTime || {};
  const et = score.extraTime || {};
  const pen = score.penalties || {};
  const winner = score.winner;
  const duration = score.duration;
  const isET = duration === "EXTRA_TIME";
  const isPen = duration === "PENALTY_SHOOTOUT";
  const homeWon = winner === "HOME_TEAM";
  const awayWon = winner === "AWAY_TEAM";

  let matchDate = "";
  let matchTime = "";
  try {
    if (m?.utcDate) {
      const d = parseISO(m.utcDate);
      matchDate = d.toLocaleDateString(dateLocale, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
      matchTime = format(d, "HH:mm");
    }
  } catch {}

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) onClose(); }}>
      <DialogContent className="max-w-lg w-[95vw] rounded-3xl border-2 border-slate-200 p-0 overflow-hidden bg-white max-h-[90vh] overflow-y-auto" data-testid="match-detail-modal">
        {loading ? (
          <div className="p-8 space-y-4">
            <Skeleton className="h-12 rounded-2xl" />
            <Skeleton className="h-32 rounded-2xl" />
            <Skeleton className="h-24 rounded-2xl" />
          </div>
        ) : !m ? (
          <div className="p-8 text-center text-slate-500 font-semibold">{t("detail.error")}</div>
        ) : (
          <>
            {/* Header */}
            <div className="bg-slate-50 border-b-2 border-slate-200 px-6 py-4 flex items-center gap-3">
              {m.competition?.emblem && <img src={m.competition.emblem} alt="" className="w-7 h-7 object-contain" />}
              <div className="flex-1 min-w-0">
                <div className="font-bold text-slate-800 text-sm">{m.competition?.name}</div>
                <div className="text-xs text-slate-400 font-semibold">
                  {m.stage && m.stage !== "REGULAR_SEASON" ? m.stage.replace(/_/g, " ") : ""}
                  {m.matchday ? ` ${t("match.matchday")} ${m.matchday}` : ""}
                </div>
              </div>
              {isLive && <span className="bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full animate-pulse-live">{t("match.live")}</span>}
              {isFinished && <span className="bg-slate-700 text-white text-xs font-bold px-3 py-1 rounded-full">{t("match.ft")}</span>}
            </div>

            {/* Score section */}
            <div className="px-6 py-6">
              <div className="flex items-center justify-between">
                {/* Home */}
                <div className={`flex flex-col items-center gap-2 flex-1 transition-opacity ${awayWon ? "opacity-50" : ""}`}>
                  {m.homeTeam?.crest && <img src={m.homeTeam.crest} alt="" className="w-16 h-16 object-contain" />}
                  <span className={`font-bold text-sm text-center leading-tight ${homeWon ? "text-slate-800" : "text-slate-600"}`}>
                    {m.homeTeam?.shortName || m.homeTeam?.name}
                  </span>
                  {homeWon && isFinished && (
                    <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-yellow-300">
                      <Trophy size={10} strokeWidth={3} /> {t("detail.winner")}
                    </span>
                  )}
                </div>

                {/* Score */}
                <div className="text-center px-4">
                  {isFinished || isLive ? (
                    <>
                      <div className="text-4xl font-black text-slate-800">
                        <span className={homeWon ? "text-green-600" : ""}>{ft.home}</span>
                        <span className="text-slate-300 mx-1">:</span>
                        <span className={awayWon ? "text-green-600" : ""}>{ft.away}</span>
                      </div>
                      {(ht.home != null && ht.away != null) && (
                        <div className="text-sm font-bold text-slate-400 mt-1">
                          {t("detail.halfTime")} {ht.home}:{ht.away}
                        </div>
                      )}
                      {/* Extra time / Penalties badges */}
                      {isET && (
                        <div className="mt-2 inline-flex items-center gap-1 bg-amber-100 text-amber-700 text-xs font-bold px-3 py-1 rounded-full border border-amber-300">
                          <Zap size={12} strokeWidth={3} />
                          {t("detail.extraTime")}
                          {et.home != null && <span className="ml-1">({et.home}:{et.away})</span>}
                        </div>
                      )}
                      {isPen && (
                        <div className="mt-2 inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-bold px-3 py-1 rounded-full border border-red-300">
                          <Zap size={12} strokeWidth={3} />
                          {t("detail.penalties")}
                          {pen.home != null && <span className="ml-1">({pen.home}:{pen.away})</span>}
                        </div>
                      )}
                    </>
                  ) : (
                    <div>
                      <div className="text-sm font-bold text-sky-500">{matchDate}</div>
                      <div className="text-3xl font-black text-slate-800 mt-1">{matchTime}</div>
                    </div>
                  )}
                </div>

                {/* Away */}
                <div className={`flex flex-col items-center gap-2 flex-1 transition-opacity ${homeWon ? "opacity-50" : ""}`}>
                  {m.awayTeam?.crest && <img src={m.awayTeam.crest} alt="" className="w-16 h-16 object-contain" />}
                  <span className={`font-bold text-sm text-center leading-tight ${awayWon ? "text-slate-800" : "text-slate-600"}`}>
                    {m.awayTeam?.shortName || m.awayTeam?.name}
                  </span>
                  {awayWon && isFinished && (
                    <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-yellow-300">
                      <Trophy size={10} strokeWidth={3} /> {t("detail.winner")}
                    </span>
                  )}
                </div>
              </div>

              {/* Timeline */}
              {isFinished && (ht.home != null) && (
                <div className="mt-6">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-400 mb-2">
                    <Clock size={14} strokeWidth={2.5} /> {t("detail.timeline")}
                  </div>
                  <div className="flex items-center gap-0">
                    <div className="flex-1 bg-slate-100 rounded-l-full h-10 flex items-center justify-center relative border-2 border-slate-200">
                      <span className="text-xs font-bold text-slate-500">{t("detail.firstHalf")}</span>
                      <span className="absolute -bottom-5 text-xs font-black text-slate-600">{ht.home}:{ht.away}</span>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-yellow-400 border-2 border-yellow-500 flex items-center justify-center z-10 -mx-1">
                      <span className="text-[10px] font-black text-white">{t("match.ht")}</span>
                    </div>
                    <div className="flex-1 bg-slate-100 rounded-r-full h-10 flex items-center justify-center relative border-2 border-slate-200">
                      <span className="text-xs font-bold text-slate-500">{t("detail.secondHalf")}</span>
                      <span className="absolute -bottom-5 text-xs font-black text-slate-600">{ft.home}:{ft.away}</span>
                    </div>
                  </div>
                  <div className="flex justify-between mt-7 text-[10px] font-bold text-slate-400">
                    <span>0'</span>
                    <span>45'</span>
                    <span>{isET ? "120'" : "90'"}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Match info */}
            <div className="px-6 pb-4 space-y-2">
              <div className="flex items-center gap-3 text-sm">
                <Calendar size={16} strokeWidth={2.5} className="text-slate-400" />
                <span className="font-semibold text-slate-600 capitalize">{matchDate}</span>
              </div>
              {m.venue && (
                <div className="flex items-center gap-3 text-sm">
                  <MapPin size={16} strokeWidth={2.5} className="text-slate-400" />
                  <span className="font-semibold text-slate-600">{m.venue}</span>
                </div>
              )}
              {m.referees?.length > 0 && (
                <div className="flex items-center gap-3 text-sm">
                  <User size={16} strokeWidth={2.5} className="text-slate-400" />
                  <span className="font-semibold text-slate-600">
                    {m.referees[0].name} ({m.referees[0].nationality})
                  </span>
                </div>
              )}
            </div>

            <MatchStorySection story={story} loading={storyLoading} error={storyError} />

            {/* Head to Head */}
            {m.h2h && m.h2h.recentMatches?.length > 0 && (
              <div className="px-6 pb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Swords size={16} strokeWidth={2.5} className="text-sky-500" />
                  <span className="font-bold text-slate-800 text-sm">{t("detail.h2h")}</span>
                  <span className="text-xs font-semibold text-slate-400 ml-auto">
                    {m.h2h.totalGoals > 0 && (
                      <span>{m.h2h.totalGoals} {t("detail.totalGoals").replace("{n}", m.h2h.totalMatches)}</span>
                    )}
                  </span>
                </div>

                {/* H2H Stats bar */}
                {m.h2h.totalMatches > 0 && (
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs font-bold text-slate-600 w-6 text-right">{m.h2h.homeWins}</span>
                    <div className="flex-1 flex h-3 rounded-full overflow-hidden">
                      <div className="bg-sky-400 transition-all" style={{ width: `${(m.h2h.homeWins / m.h2h.totalMatches) * 100}%` }} />
                      <div className="bg-slate-300 transition-all" style={{ width: `${(m.h2h.draws / m.h2h.totalMatches) * 100}%` }} />
                      <div className="bg-orange-400 transition-all" style={{ width: `${(m.h2h.awayWins / m.h2h.totalMatches) * 100}%` }} />
                    </div>
                    <span className="text-xs font-bold text-slate-600 w-6">{m.h2h.awayWins}</span>
                  </div>
                )}

                {/* Recent matches */}
                <div className="space-y-2">
                  {m.h2h.recentMatches.map((rm, i) => {
                    let dateStr = "";
                    try { dateStr = format(parseISO(rm.date), "dd.MM.yy"); } catch {}
                    return (
                      <div key={i} className="flex items-center gap-2 bg-slate-50 rounded-2xl p-3 text-sm" data-testid={`h2h-match-${i}`}>
                        <span className="text-xs text-slate-400 font-semibold w-16">{dateStr}</span>
                        <div className="flex items-center gap-1.5 flex-1 min-w-0 justify-end">
                          <span className="font-bold text-slate-700 truncate text-right text-xs">{rm.homeTeam}</span>
                          {rm.homeCrest && <img src={rm.homeCrest} alt="" className="w-4 h-4 object-contain flex-shrink-0" />}
                        </div>
                        <span className="font-black text-slate-800 px-2 text-sm min-w-[40px] text-center">
                          {rm.homeScore}:{rm.awayScore}
                        </span>
                        <div className="flex items-center gap-1.5 flex-1 min-w-0">
                          {rm.awayCrest && <img src={rm.awayCrest} alt="" className="w-4 h-4 object-contain flex-shrink-0" />}
                          <span className="font-bold text-slate-700 truncate text-xs">{rm.awayTeam}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
