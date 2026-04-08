import { format, parseISO, isToday, isTomorrow } from "date-fns";
import { useLanguage } from "@/contexts/LanguageContext";

export default function MatchCard({ match }) {
  const { t, dateLocale } = useLanguage();
  const isLive = match.status === "IN_PLAY" || match.status === "PAUSED";
  const isFinished = match.status === "FINISHED";

  const ft = match.score?.fullTime || {};
  const homeScore = isLive ? (match.score?.fullTime?.home ?? match.score?.halfTime?.home ?? "-") : ft.home;
  const awayScore = isLive ? (match.score?.fullTime?.away ?? match.score?.halfTime?.away ?? "-") : ft.away;

  let dateLabel = "";
  let timeLabel = "";
  try {
    const d = parseISO(match.utcDate);
    dateLabel = isToday(d) ? t("match.today") : isTomorrow(d) ? t("match.tomorrow") : format(d, "MMM d");
    timeLabel = format(d, "HH:mm");
  } catch {
    dateLabel = "";
    timeLabel = "";
  }

  return (
    <div
      data-testid={`match-card-${match.id}`}
      className={`card-tactile p-4 ${isLive ? "border-green-400" : ""}`}
    >
      <div className="flex items-center gap-2 mb-3">
        {match.competition?.emblem && (
          <img src={match.competition.emblem} alt="" className="w-5 h-5 object-contain" />
        )}
        <span className="text-xs font-bold uppercase tracking-widest text-slate-400 truncate">
          {match.competition?.name}
        </span>
        {isLive && (
          <span className="ml-auto bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full animate-pulse-live flex-shrink-0">
            {t("match.live")}
          </span>
        )}
        {isFinished && (
          <span className="ml-auto bg-slate-700 text-white text-xs font-bold px-2.5 py-1 rounded-full flex-shrink-0">
            {t("match.ft")}
          </span>
        )}
        {match.status === "PAUSED" && (
          <span className="ml-auto bg-yellow-500 text-white text-xs font-bold px-2.5 py-1 rounded-full flex-shrink-0">
            {t("match.ht")}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5 flex-1 min-w-0">
          {match.homeTeam?.crest && (
            <img src={match.homeTeam.crest} alt="" className="w-9 h-9 object-contain flex-shrink-0" />
          )}
          <span className="font-bold text-sm text-slate-800 truncate">
            {match.homeTeam?.shortName || match.homeTeam?.name}
          </span>
        </div>

        <div className="px-3 text-center min-w-[80px] flex-shrink-0">
          {isFinished || isLive ? (
            <span className="text-2xl font-black text-slate-800">
              {homeScore} <span className="text-slate-400">-</span> {awayScore}
            </span>
          ) : (
            <div>
              <div className="text-xs font-bold text-sky-500">{dateLabel}</div>
              <div className="text-lg font-black text-slate-700">{timeLabel}</div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2.5 flex-1 min-w-0 justify-end">
          <span className="font-bold text-sm text-slate-800 truncate text-right">
            {match.awayTeam?.shortName || match.awayTeam?.name}
          </span>
          {match.awayTeam?.crest && (
            <img src={match.awayTeam.crest} alt="" className="w-9 h-9 object-contain flex-shrink-0" />
          )}
        </div>
      </div>

      {match.matchday && (
        <div className="text-center text-xs text-slate-400 font-semibold mt-2">
          {t("match.matchday")} {match.matchday}
        </div>
      )}
    </div>
  );
}
