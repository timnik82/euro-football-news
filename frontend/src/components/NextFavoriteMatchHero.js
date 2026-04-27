import { useEffect, useState } from "react";
import { Clock, Sparkles } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

function getTimeParts(targetDate) {
  const diffMs = targetDate.getTime() - Date.now();
  if (diffMs <= 0) return { live: true };
  const totalSeconds = Math.floor(diffMs / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return { days, hours, minutes, seconds, live: false };
}

export default function NextFavoriteMatchHero({ match, favoriteTeam, onClick }) {
  const { t, dateLocale } = useLanguage();
  const target = new Date(match.utcDate);
  const [parts, setParts] = useState(() => getTimeParts(target));

  useEffect(() => {
    const id = setInterval(() => setParts(getTimeParts(target)), 1000);
    return () => clearInterval(id);
  }, [match.utcDate]);

  const isHome = String(match.homeTeam?.id) === favoriteTeam.item_id;
  const opponent = isHome ? match.awayTeam : match.homeTeam;
  const venueLabel = isHome ? t("nextMatch.home") : t("nextMatch.away");
  const niceDate = target.toLocaleDateString(dateLocale, {
    weekday: "long", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit",
  });

  return (
    <button
      data-testid="next-favorite-match-hero"
      onClick={() => onClick(match.id)}
      className="w-full text-left card-tactile mb-6 overflow-hidden p-0 animate-slide-up"
    >
      <div className="relative bg-gradient-to-br from-sky-500 via-sky-600 to-indigo-700 text-white p-6 sm:p-8">
        <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/10 blur-2xl" />
        <div className="absolute -left-10 -bottom-12 w-44 h-44 rounded-full bg-yellow-300/20 blur-3xl" />

        <div className="relative flex items-center gap-2 mb-4">
          <Sparkles size={18} strokeWidth={2.5} className="text-yellow-300" />
          <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-white/90">
            {t("nextMatch.title")}
          </span>
        </div>

        <div className="relative flex items-center gap-4 sm:gap-6 mb-5 flex-wrap">
          <div className="flex items-center gap-3 min-w-0">
            {favoriteTeam.crest && (
              <img src={favoriteTeam.crest} alt="" className="w-14 h-14 sm:w-16 sm:h-16 object-contain bg-white/15 rounded-2xl p-1" />
            )}
            <div className="min-w-0">
              <div className="text-lg sm:text-2xl font-black truncate">{favoriteTeam.name}</div>
              <div className="text-xs font-bold text-white/70 uppercase tracking-wider">{venueLabel}</div>
            </div>
          </div>

          <div className="text-2xl sm:text-3xl font-black text-white/40 px-2">vs</div>

          <div className="flex items-center gap-3 min-w-0">
            {opponent?.crest && (
              <img src={opponent.crest} alt="" className="w-12 h-12 sm:w-14 sm:h-14 object-contain bg-white/15 rounded-2xl p-1" />
            )}
            <div className="text-base sm:text-xl font-bold truncate">
              {opponent?.shortName || opponent?.name}
            </div>
          </div>
        </div>

        <div className="relative flex items-center gap-2 text-white/85 mb-4">
          <Clock size={14} strokeWidth={2.5} />
          <span className="text-xs sm:text-sm font-semibold capitalize">{niceDate}</span>
        </div>

        {parts.live ? (
          <div className="relative inline-flex items-center gap-2 bg-red-500 px-4 py-2 rounded-full">
            <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
            <span className="font-black text-sm tracking-widest">{t("match.live")}</span>
          </div>
        ) : (
          <div className="relative grid grid-cols-4 gap-2 sm:gap-3 max-w-md">
            <CountdownChip value={parts.days} label={t("nextMatch.days")} />
            <CountdownChip value={parts.hours} label={t("nextMatch.hours")} />
            <CountdownChip value={parts.minutes} label={t("nextMatch.minutes")} />
            <CountdownChip value={parts.seconds} label={t("nextMatch.seconds")} />
          </div>
        )}
      </div>
    </button>
  );
}

function CountdownChip({ value, label }) {
  const display = String(value).padStart(2, "0");
  return (
    <div className="bg-white/15 backdrop-blur-sm rounded-2xl py-2 px-1 sm:py-3 text-center border border-white/20">
      <div className="text-2xl sm:text-3xl font-black tabular-nums leading-none">{display}</div>
      <div className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-white/70 mt-1">{label}</div>
    </div>
  );
}
