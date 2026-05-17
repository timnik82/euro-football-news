import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Activity, ArrowLeft, RefreshCw, ShieldCheck, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { BrandHeading } from "@/components/BrandHeading";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useLanguage } from "@/contexts/LanguageContext";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const statusStyles = {
  matched: "bg-emerald-100 text-emerald-700 border-emerald-200",
  source_found: "bg-emerald-100 text-emerald-700 border-emerald-200",
  no_match: "bg-amber-100 text-amber-700 border-amber-200",
  no_results: "bg-slate-100 text-slate-600 border-slate-200",
  skipped: "bg-slate-100 text-slate-600 border-slate-200",
  failed: "bg-red-100 text-red-700 border-red-200",
  fallback: "bg-orange-100 text-orange-700 border-orange-200",
  not_checked: "bg-sky-100 text-sky-700 border-sky-200",
};

function StatusPill({ status, label, testId }) {
  return (
    <span
      data-testid={testId}
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-black ${statusStyles[status] || statusStyles.no_results}`}
    >
      {label}
    </span>
  );
}

function FieldStat({ label, value, testId }) {
  const displayValue = value ?? 0;
  const compactText = String(displayValue).length > 10;
  return (
    <div data-testid={testId} className="min-w-[76px] rounded-2xl bg-white/80 border border-slate-200 px-3 py-2">
      <div className="text-[10px] font-black uppercase text-slate-400 leading-none">{label}</div>
      <div className={`${compactText ? "text-xs" : "text-sm"} font-black text-slate-800 mt-1 break-words leading-tight`}>
        {displayValue}
      </div>
    </div>
  );
}

function ProviderRow({ diagnostic, matchId, index, t }) {
  const status = diagnostic.status || "no_results";
  return (
    <div
      data-testid={`admin-provider-row-${matchId}-${index}`}
      className="border-t border-slate-200 py-3 first:border-t-0 first:pt-0 last:pb-0"
    >
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 data-testid={`admin-provider-name-${matchId}-${index}`} className="text-sm font-black text-slate-800 truncate">
              {diagnostic.sourceName || diagnostic.provider}
            </h3>
            <StatusPill
              status={status}
              label={t(`admin.status.${status}`)}
              testId={`admin-provider-status-${matchId}-${index}`}
            />
          </div>
          <p data-testid={`admin-provider-message-${matchId}-${index}`} className="text-xs font-semibold text-slate-500 mt-1 leading-relaxed">
            {diagnostic.error || diagnostic.message || "—"}
          </p>
        </div>
        {diagnostic.httpStatus && (
          <span data-testid={`admin-provider-http-${matchId}-${index}`} className="text-xs font-black text-slate-400 whitespace-nowrap">
            HTTP {diagnostic.httpStatus}
          </span>
        )}
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <FieldStat label={t("admin.queries")} value={diagnostic.queryCount} testId={`admin-provider-queries-${matchId}-${index}`} />
        <FieldStat label={t("admin.candidates")} value={diagnostic.candidateCount} testId={`admin-provider-candidates-${matchId}-${index}`} />
        <FieldStat label={t("admin.matches")} value={diagnostic.matchedCount} testId={`admin-provider-matches-${matchId}-${index}`} />
      </div>
    </div>
  );
}

export default function AdminStoryDiagnosticsPage() {
  const navigate = useNavigate();
  const { t, language, dateLocale } = useLanguage();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshingId, setRefreshingId] = useState(null);

  const fetchDiagnostics = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/admin/story-diagnostics`, {
        params: { lang: language, limit: 10 },
        withCredentials: true,
      });
      setMatches(data.matches || []);
    } catch (err) {
      setError(t("admin.loadError"));
      toast.error(t("admin.loadError"));
    } finally {
      setLoading(false);
    }
  }, [language, t]);

  useEffect(() => {
    fetchDiagnostics();
  }, [fetchDiagnostics]);

  const stats = useMemo(() => {
    const checked = matches.filter((match) => match.storyStatus !== "not_checked").length;
    const sourced = matches.filter((match) => match.storyStatus === "source_found").length;
    const fallback = matches.filter((match) => match.storyStatus === "fallback").length;
    return { checked, sourced, fallback };
  }, [matches]);

  const refreshMatch = async (matchId) => {
    setRefreshingId(matchId);
    try {
      const { data } = await axios.post(`${API}/admin/story-diagnostics/${matchId}/refresh`, null, {
        params: { lang: language },
        withCredentials: true,
      });
      setMatches((current) => current.map((item) => (item.matchId === matchId ? data : item)));
      toast.success(t("admin.refreshDone"));
    } catch (err) {
      toast.error(t("admin.refreshError"));
    } finally {
      setRefreshingId(null);
    }
  };

  return (
    <div data-testid="admin-story-diagnostics-page" className="max-w-6xl mx-auto px-4 pt-6 pb-6">
      <div className="mb-6 flex flex-col md:flex-row md:items-start md:justify-between gap-4 animate-slide-up">
        <div>
          <button
            data-testid="admin-back-button"
            type="button"
            onClick={() => navigate("/")}
            className="inline-flex items-center gap-2 text-sm font-black text-slate-500 hover:text-sky-600 transition-colors mb-3"
          >
            <ArrowLeft size={18} strokeWidth={3} /> {t("admin.back")}
          </button>
          <BrandHeading label={t("admin.title")} size="lg" testId="admin-brand-heading" />
          <p data-testid="admin-subtitle" className="text-base sm:text-lg font-semibold text-slate-500 mt-1 max-w-2xl">
            {t("admin.subtitle")}
          </p>
        </div>
        <Button
          data-testid="admin-refresh-list-button"
          type="button"
          onClick={fetchDiagnostics}
          disabled={loading}
          className="btn-chunky bg-slate-900 hover:bg-slate-700 text-white min-h-12 px-5"
        >
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} /> {t("admin.refreshList")}
        </Button>
      </div>

      <section data-testid="admin-summary-strip" className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6 animate-slide-up" style={{ animationDelay: "0.04s" }}>
        <div className="rounded-3xl bg-sky-100 border-2 border-sky-200 p-4">
          <p className="text-xs font-black uppercase text-sky-600">{t("admin.checked")}</p>
          <p data-testid="admin-checked-count" className="text-3xl font-black text-slate-900">{stats.checked}</p>
        </div>
        <div className="rounded-3xl bg-emerald-100 border-2 border-emerald-200 p-4">
          <p className="text-xs font-black uppercase text-emerald-700">{t("admin.sourceFound")}</p>
          <p data-testid="admin-source-count" className="text-3xl font-black text-slate-900">{stats.sourced}</p>
        </div>
        <div className="rounded-3xl bg-orange-100 border-2 border-orange-200 p-4">
          <p className="text-xs font-black uppercase text-orange-700">{t("admin.fallbackStories")}</p>
          <p data-testid="admin-fallback-count" className="text-3xl font-black text-slate-900">{stats.fallback}</p>
        </div>
      </section>

      {error && (
        <div data-testid="admin-error-message" className="mb-4 rounded-3xl border-2 border-red-200 bg-red-50 p-4 text-sm font-bold text-red-600">
          {error}
        </div>
      )}

      {loading ? (
        <div data-testid="admin-loading-list" className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((item) => <Skeleton key={item} className="h-72 rounded-3xl" />)}
        </div>
      ) : (
        <div data-testid="admin-match-list" className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {matches.map((match, index) => {
            const generatedAt = match.generatedAt
              ? new Date(match.generatedAt).toLocaleString(dateLocale, { dateStyle: "medium", timeStyle: "short" })
              : t("admin.neverChecked");
            const score = match.score?.home != null && match.score?.away != null ? `${match.score.home}:${match.score.away}` : "—";
            return (
              <article
                key={match.matchId}
                data-testid={`admin-match-card-${match.matchId}`}
                className="card-tactile p-5 animate-slide-up"
                style={{ animationDelay: `${0.06 + index * 0.03}s` }}
              >
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <ShieldCheck size={18} className="text-sky-500" />
                      <span data-testid={`admin-match-competition-${match.matchId}`} className="text-[11px] font-black uppercase text-slate-400 truncate">
                        {match.competition || match.competitionCode || "—"}
                      </span>
                    </div>
                    <h2 data-testid={`admin-match-label-${match.matchId}`} className="text-xl font-black text-slate-900 leading-tight">
                      {match.label}
                    </h2>
                  </div>
                  <StatusPill
                    status={match.storyStatus}
                    label={t(`admin.status.${match.storyStatus}`)}
                    testId={`admin-match-story-status-${match.matchId}`}
                  />
                </div>

                <div className="grid grid-cols-3 gap-2 mb-4">
                  <FieldStat label={t("admin.score")} value={score} testId={`admin-match-score-${match.matchId}`} />
                  <FieldStat label={t("admin.sources")} value={match.sourceCount} testId={`admin-match-source-count-${match.matchId}`} />
                  <FieldStat label={t("admin.updated")} value={generatedAt} testId={`admin-match-generated-${match.matchId}`} />
                </div>

                <div data-testid={`admin-provider-list-${match.matchId}`} className="rounded-3xl bg-slate-50/70 border border-slate-200 p-4 mb-4">
                  {match.diagnostics?.length ? (
                    match.diagnostics.map((diagnostic, providerIndex) => (
                      <ProviderRow
                        key={`${diagnostic.provider}-${diagnostic.sourceName}-${providerIndex}`}
                        diagnostic={diagnostic}
                        matchId={match.matchId}
                        index={providerIndex}
                        t={t}
                      />
                    ))
                  ) : (
                    <p data-testid={`admin-no-diagnostics-${match.matchId}`} className="text-sm font-bold text-slate-500">
                      {t("admin.noDiagnostics")}
                    </p>
                  )}
                </div>

                <Button
                  data-testid={`admin-refresh-match-button-${match.matchId}`}
                  type="button"
                  onClick={() => refreshMatch(match.matchId)}
                  disabled={refreshingId === match.matchId}
                  className="w-full btn-chunky bg-sky-500 hover:bg-sky-600 text-white min-h-12"
                >
                  {refreshingId === match.matchId ? (
                    <><RefreshCw size={18} className="animate-spin" /> {t("admin.checking")}</>
                  ) : (
                    <><Sparkles size={18} /> {t("admin.refreshMatch")}</>
                  )}
                </Button>
              </article>
            );
          })}

          {matches.length === 0 && (
            <div data-testid="admin-empty-state" className="lg:col-span-2 rounded-3xl border-2 border-slate-200 bg-white p-10 text-center">
              <Activity size={42} className="mx-auto text-slate-300 mb-3" />
              <p className="text-lg font-black text-slate-600">{t("admin.empty")}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}