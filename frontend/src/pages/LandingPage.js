import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { format, parseISO } from "date-fns";
import { useLanguage } from "@/contexts/LanguageContext";
import { BrandHeading } from "@/components/BrandHeading";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const HERO_VIDEO = "/media/hero.mp4";
const HERO_POSTER = "/media/hero-poster.jpg";

function HeroMedia() {
  const [videoEnabled, setVideoEnabled] = useState(false);
  const [videoReady, setVideoReady] = useState(false);

  useEffect(() => {
    const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const connection = navigator.connection;
    const slowConnection =
      connection?.saveData || ["slow-2g", "2g"].includes(connection?.effectiveType);
    if (!reducedMotion && !slowConnection) setVideoEnabled(true);
  }, []);

  return (
    <>
      {/* Always rendered first so it's the LCP element and the immediate
          fallback if the video is disabled, still loading, or fails. */}
      <img
        src={HERO_POSTER}
        alt=""
        width="1920"
        height="1080"
        fetchPriority="high"
        decoding="async"
        className="absolute inset-0 w-full h-full object-cover"
      />
      {videoEnabled && (
        <video
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          poster={HERO_POSTER}
          onCanPlay={() => setVideoReady(true)}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ${
            videoReady ? "opacity-100" : "opacity-0"
          }`}
        >
          <source src={HERO_VIDEO} type="video/mp4" />
        </video>
      )}
    </>
  );
}

function ScorePreviewRow({ match, showDate }) {
  const isLive = match.status === "IN_PLAY" || match.status === "PAUSED";
  const isFinished = match.status === "FINISHED";
  const ft = match.score?.fullTime || {};
  const homeScore = isLive ? (ft.home ?? match.score?.halfTime?.home ?? "-") : ft.home;
  const awayScore = isLive ? (ft.away ?? match.score?.halfTime?.away ?? "-") : ft.away;
  let timeLabel = "";
  try {
    const d = parseISO(match.utcDate);
    timeLabel = showDate ? format(d, "EEE HH:mm") : format(d, "HH:mm");
  } catch {
    timeLabel = "";
  }

  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-100 last:border-b-0">
      <div className="flex items-center gap-2 flex-1 min-w-0">
        {match.homeTeam?.crest && (
          <img src={match.homeTeam.crest} alt="" className="w-6 h-6 object-contain flex-shrink-0" />
        )}
        <span className="font-bold text-sm text-slate-800 truncate">
          {match.homeTeam?.shortName || match.homeTeam?.name}
        </span>
      </div>
      <div className="px-3 flex-shrink-0">
        {isFinished || isLive ? (
          <span className="font-black text-sky-500">
            {homeScore} - {awayScore}
          </span>
        ) : (
          <span className="text-xs font-bold text-slate-400">{timeLabel}</span>
        )}
      </div>
      <div className="flex items-center gap-2 flex-1 min-w-0 justify-end">
        <span className="font-bold text-sm text-slate-800 truncate text-right">
          {match.awayTeam?.shortName || match.awayTeam?.name}
        </span>
        {match.awayTeam?.crest && (
          <img src={match.awayTeam.crest} alt="" className="w-6 h-6 object-contain flex-shrink-0" />
        )}
      </div>
    </div>
  );
}

export default function LandingPage({ onEnter }) {
  const { t } = useLanguage();
  const [previewMatches, setPreviewMatches] = useState([]);
  const [previewLoading, setPreviewLoading] = useState(true);
  const [isUpcomingPreview, setIsUpcomingPreview] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadPreview = async () => {
      let todayMatches = [];
      try {
        const { data } = await axios.get(`${API}/matches/today`);
        todayMatches = data || [];
      } catch {
        // /matches/today failing shouldn't block trying /matches/upcoming below.
      }
      if (cancelled) return;

      if (todayMatches.length) {
        setPreviewMatches(todayMatches.slice(0, 3));
        setIsUpcomingPreview(false);
        setPreviewLoading(false);
        return;
      }

      try {
        const { data } = await axios.get(`${API}/matches/upcoming`);
        if (cancelled) return;
        setPreviewMatches(data.slice(0, 3));
        setIsUpcomingPreview(true);
      } catch {
        // Both requests failed; the empty state below covers this.
      } finally {
        if (!cancelled) setPreviewLoading(false);
      }
    };

    loadPreview();
    // A visitor can sit on this hero for a while before clicking through,
    // so refresh periodically - otherwise a match that kicks off or ends
    // while the page is open would show a stale score indefinitely.
    const intervalId = setInterval(loadPreview, 60000);
    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, []);

  const liveCount = previewMatches.filter(
    (m) => m.status === "IN_PLAY" || m.status === "PAUSED"
  ).length;

  return (
    <div className="relative min-h-[70vh] sm:min-h-[85vh] overflow-hidden rounded-b-[2.5rem]">
      <HeroMedia />
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/85 via-slate-900/45 to-slate-900/20" />

      <div className="relative z-10 flex items-center justify-between px-5 sm:px-8 pt-6">
        <BrandHeading label="Goal Kick" size="sm" textClassName="text-white" />
        <Link
          to="/login"
          className="bg-white/15 border border-white/40 text-white text-sm font-bold px-4 py-2 rounded-full"
          data-testid="landing-signin-link"
        >
          {t("nav.login")}
        </Link>
      </div>

      <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-8 px-5 sm:px-8 pb-10 pt-16 md:pt-24">
        <div className="max-w-md text-white animate-slide-up">
          <h1 className="text-4xl sm:text-5xl font-black leading-tight tracking-tight mb-3">
            {t("landing.headline")}
          </h1>
          <p className="text-base sm:text-lg text-slate-200 font-medium mb-6">
            {t("landing.subheadline")}
          </p>
          <button
            onClick={onEnter}
            className="bg-accent text-accent-foreground font-black text-base px-6 py-3.5 rounded-2xl shadow-[0_14px_30px_rgba(34,197,94,0.35)] animate-bounce-in"
            data-testid="landing-enter-btn"
          >
            {t("landing.cta")}
          </button>
        </div>

        <div className="card-tactile p-4 w-full md:w-80 flex-shrink-0" data-testid="landing-score-preview">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-black uppercase tracking-widest text-slate-400">
              {isUpcomingPreview ? t("landing.upcomingLabel") : t("landing.todayLabel")}
            </h3>
            {liveCount > 0 && (
              <span className="text-red-500 text-xs font-bold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse-live" />
                {liveCount} {t("match.live")}
              </span>
            )}
          </div>
          {previewLoading ? (
            <p className="text-sm text-slate-400 font-semibold py-2">{t("landing.previewLoading")}</p>
          ) : previewMatches.length > 0 ? (
            previewMatches.map((m) => (
              <ScorePreviewRow key={m.id} match={m} showDate={isUpcomingPreview} />
            ))
          ) : (
            <p className="text-sm text-slate-400 font-semibold py-2">{t("landing.previewEmpty")}</p>
          )}
        </div>
      </div>
    </div>
  );
}
