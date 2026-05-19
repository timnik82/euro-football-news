import { BookOpen, ExternalLink, Film, Sparkles } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useLanguage } from "@/contexts/LanguageContext";

function shortSnippet(value) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (text.length <= 180) return text;
  return `${text.slice(0, 177).trim()}…`;
}

export default function MatchStorySection({ story, loading, error }) {
  const { t } = useLanguage();
  const sourceSnippets = (story?.sources || []).filter((source) => source.description && source.url).slice(0, 3);

  if (loading) {
    return (
      <section className="px-6 pb-6" data-testid="match-story-loading-section">
        <div className="rounded-3xl border-2 border-orange-100 bg-orange-50/70 p-4">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={18} className="text-orange-500 animate-pulse" />
            <span className="font-bold text-slate-800 text-sm" data-testid="match-story-loading-text">
              {t("matchStory.loading")}
            </span>
          </div>
          <Skeleton className="h-5 rounded-xl mb-2" />
          <Skeleton className="h-16 rounded-2xl" />
        </div>
      </section>
    );
  }

  if (error || !story) {
    return (
      <section className="px-6 pb-6" data-testid="match-story-error-section">
        <div className="rounded-3xl border-2 border-slate-100 bg-slate-50 p-4">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen size={18} className="text-slate-400" />
            <span className="font-bold text-slate-800 text-sm">{t("matchStory.title")}</span>
          </div>
          <p className="text-sm font-semibold text-slate-500" data-testid="match-story-error-text">
            {t("matchStory.error")}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="px-6 pb-6" data-testid="match-story-section">
      <div className="rounded-3xl border-2 border-orange-100 bg-gradient-to-br from-orange-50 via-white to-sky-50 overflow-hidden">
        {story.imageUrl && (
          <div className="aspect-[16/9] bg-slate-100 overflow-hidden" data-testid="match-story-image-wrap">
            <img
              src={story.imageUrl}
              alt=""
              className="w-full h-full object-cover"
              data-testid="match-story-image"
              loading="lazy"
            />
          </div>
        )}
        <div className="p-4 space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <BookOpen size={18} strokeWidth={2.5} className="text-orange-500" />
              <span className="font-black text-slate-800 text-sm" data-testid="match-story-section-title">
                {t("matchStory.title")}
              </span>
              {story.isFallback && (
                <span className="ml-auto text-[10px] font-bold bg-white text-orange-500 border border-orange-200 rounded-full px-2 py-1" data-testid="match-story-fallback-badge">
                  {t("matchStory.fallbackBadge")}
                </span>
              )}
            </div>
            <h3 className="text-lg font-black text-slate-900 leading-tight" data-testid="match-story-headline">
              {story.title}
            </h3>
            <p className="text-sm font-semibold text-slate-600 mt-2 leading-relaxed" data-testid="match-story-summary">
              {story.summary}
            </p>
          </div>

          {story.keyPoints?.length > 0 && (
            <ul className="space-y-2" data-testid="match-story-key-points">
              {story.keyPoints.map((point, index) => (
                <li key={`${point}-${index}`} className="flex gap-2 text-sm font-semibold text-slate-700" data-testid={`match-story-key-point-${index}`}>
                  <span className="mt-1 h-2 w-2 rounded-full bg-sky-400 flex-shrink-0" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          )}

          {story.videoUrl && (
            <a
              href={story.videoUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-full bg-slate-900 text-white px-4 py-2 text-sm font-bold hover:bg-slate-700 transition-colors"
              data-testid="match-story-video-link"
            >
              <Film size={16} /> {t("matchStory.watchHighlights")}
            </a>
          )}

          {sourceSnippets.length > 0 && (
            <div data-testid="match-story-source-snippets-section" className="rounded-2xl bg-white/80 border border-slate-200 p-3">
              <div className="text-xs font-black uppercase text-slate-400 mb-3" data-testid="match-story-source-snippets-label">
                {t("matchStory.sourceSnippets")}
              </div>
              <div className="space-y-3">
                {sourceSnippets.map((source, index) => (
                  <a
                    key={source.url || index}
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-2xl bg-slate-50 border border-slate-200 p-3 hover:border-sky-300 hover:bg-sky-50 transition-colors"
                    data-testid={`match-story-source-snippet-link-${index}`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-[11px] font-black uppercase text-orange-500" data-testid={`match-story-source-snippet-source-${index}`}>
                        {source.sourceName || t("matchStory.source")}
                      </span>
                      <ExternalLink size={13} className="text-slate-400 flex-shrink-0" />
                    </div>
                    <p className="text-sm font-black text-slate-800 leading-snug" data-testid={`match-story-source-snippet-title-${index}`}>
                      {source.title}
                    </p>
                    <p className="text-xs font-semibold text-slate-600 mt-1 leading-relaxed" data-testid={`match-story-source-snippet-description-${index}`}>
                      {shortSnippet(source.description)}
                    </p>
                  </a>
                ))}
              </div>
            </div>
          )}

          {story.sources?.length > 0 && (
            <div data-testid="match-story-sources-section">
              <div className="text-xs font-black uppercase text-slate-400 mb-2" data-testid="match-story-sources-label">
                {t("matchStory.sources")}
              </div>
              <div className="flex flex-wrap gap-2">
                {story.sources.map((source, index) => (
                  <a
                    key={source.url || index}
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-3 py-1.5 text-xs font-bold text-slate-600 hover:border-sky-300 hover:text-sky-600 transition-colors"
                    data-testid={`match-story-source-link-${index}`}
                  >
                    {source.sourceName || t("matchStory.source")} <ExternalLink size={12} />
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}