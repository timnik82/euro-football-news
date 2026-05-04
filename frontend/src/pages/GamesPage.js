import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { useLanguage } from "@/contexts/LanguageContext";
import { BrandHeading } from "@/components/BrandHeading";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, Flame, Gamepad2, Lock, Medal, RotateCcw, ShieldQuestion, Sparkles, Target, Trophy, XCircle } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function GamesPage() {
  const { t, language } = useLanguage();
  const [quizzes, setQuizzes] = useState({ player: null, crest: null });
  const [profile, setProfile] = useState(null);
  const [selectedOptions, setSelectedOptions] = useState({ player: "", crest: "" });
  const [results, setResults] = useState({ player: null, crest: null });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState({ player: false, crest: false });

  useEffect(() => {
    fetchGameData();
  }, [language]);

  const fetchGameData = async () => {
    setLoading(true);
    setResults({ player: null, crest: null });
    setSelectedOptions({ player: "", crest: "" });
    try {
      const [playerQuizRes, crestQuizRes, profileRes] = await Promise.all([
        axios.get(`${API}/gamification/daily-quiz?lang=${language}`),
        axios.get(`${API}/gamification/crest-quiz?lang=${language}`),
        axios.get(`${API}/gamification/profile?lang=${language}`, { withCredentials: true }),
      ]);
      const nextQuizzes = { player: playerQuizRes.data, crest: crestQuizRes.data };
      const nextSelections = { player: "", crest: "" };
      const nextResults = { player: null, crest: null };
      setProfile(profileRes.data);
      setQuizzes(nextQuizzes);
      Object.entries(nextQuizzes).forEach(([mode, quiz]) => {
        const attempt = profileRes.data.recentAttempts?.find((item) => item.quizId === quiz.quizId);
        if (attempt) {
          nextSelections[mode] = attempt.selectedOptionId;
          nextResults[mode] = { ...attempt, alreadyAnswered: true, explanation: t("games.alreadyPlayed") };
        }
      });
      setSelectedOptions(nextSelections);
      setResults(nextResults);
    } catch (error) {
      toast.error(t("games.loadError"));
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (mode) => {
    const quiz = quizzes[mode];
    const selectedOptionId = selectedOptions[mode];
    if (!selectedOptionId || !quiz || results[mode]) return;
    setSubmitting((current) => ({ ...current, [mode]: true }));
    try {
      const endpoint = mode === "crest" ? "crest-quiz" : "daily-quiz";
      const { data } = await axios.post(
        `${API}/gamification/${endpoint}/answer`,
        { quizId: quiz.quizId, selectedOptionId, language },
        { withCredentials: true }
      );
      setResults((current) => ({ ...current, [mode]: data }));
      setProfile(data.profile);
      toast.success(data.isCorrect ? t("games.correctToast") : t("games.tryTomorrow"));
    } catch (error) {
      toast.error(t("games.submitError"));
    } finally {
      setSubmitting((current) => ({ ...current, [mode]: false }));
    }
  };

  const selectOption = (mode, optionId) => {
    if (results[mode]) return;
    setSelectedOptions((current) => ({ ...current, [mode]: optionId }));
  };

  const unlockedCount = useMemo(() => profile?.badges?.filter((badge) => badge.unlocked).length || 0, [profile]);

  return (
    <div className="max-w-5xl mx-auto px-4 pt-6 pb-4">
      <div className="mb-6 animate-slide-up space-y-3">
        <BrandHeading label="Goal Kick" size="sm" testId="games-page-brand-heading" />
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-400 border-2 border-emerald-600 flex items-center justify-center shadow-[0_5px_0_#047857]">
              <Gamepad2 size={25} strokeWidth={2.8} className="text-white" />
            </div>
            <div>
              <h1 data-testid="games-page-title" className="text-4xl sm:text-5xl font-black text-slate-800 tracking-tight">
                {t("games.title")}
              </h1>
              <p data-testid="games-page-subtitle" className="text-base sm:text-lg font-semibold text-slate-500 mt-1">
                {t("games.subtitle")}
              </p>
            </div>
          </div>
          <button
            data-testid="games-refresh-button"
            onClick={fetchGameData}
            className="w-12 h-12 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center hover:bg-slate-50 transition-colors"
            aria-label={t("games.refresh")}
          >
            <RotateCcw size={18} strokeWidth={2.6} className="text-slate-500" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-[1.25fr_0.75fr] gap-5">
          <Skeleton className="h-[390px] rounded-3xl" />
          <Skeleton className="h-[390px] rounded-3xl" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[1.25fr_0.75fr] gap-5 items-start">
          <div className="space-y-5">
            <QuizCard
              mode="player"
              testPrefix="daily-quiz"
              quiz={quizzes.player}
              selectedOptionId={selectedOptions.player}
              result={results.player}
              submitting={submitting.player}
              onSelect={selectOption}
              onSubmit={submitAnswer}
              title={t("games.guessPlayer")}
              kicker={t("games.dailyQuiz")}
              icon={<Target size={30} strokeWidth={3} className="flex-shrink-0" />}
              gradient="from-emerald-400 via-sky-400 to-yellow-300"
              t={t}
            />
            <QuizCard
              mode="crest"
              testPrefix="crest-quiz"
              quiz={quizzes.crest}
              selectedOptionId={selectedOptions.crest}
              result={results.crest}
              submitting={submitting.crest}
              onSelect={selectOption}
              onSubmit={submitAnswer}
              title={t("games.guessCrest")}
              kicker={t("games.crestQuiz")}
              icon={<ShieldQuestion size={30} strokeWidth={3} className="flex-shrink-0" />}
              gradient="from-orange-400 via-rose-400 to-sky-400"
              t={t}
              visual={quizzes.crest?.crestUrl}
            />
          </div>

          <aside className="space-y-5 animate-slide-up" style={{ animationDelay: "0.05s" }}>
            <section className="card-tactile p-5" data-testid="game-profile-card">
              <div className="flex items-center gap-2 mb-4">
                <Trophy size={22} strokeWidth={2.8} className="text-yellow-500" />
                <h2 className="text-2xl font-black text-slate-800">{t("games.scoreboard")}</h2>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl bg-sky-50 border-2 border-sky-100 p-4">
                  <p className="text-xs font-black uppercase text-slate-400">{t("games.points")}</p>
                  <p data-testid="game-profile-points" className="text-3xl font-black text-sky-500">{profile?.totalPoints || 0}</p>
                </div>
                <div className="rounded-2xl bg-orange-50 border-2 border-orange-100 p-4">
                  <p className="text-xs font-black uppercase text-slate-400">{t("games.streak")}</p>
                  <p data-testid="game-profile-streak" className="text-3xl font-black text-orange-500 flex items-center gap-1">
                    {profile?.currentStreak || 0}<Flame size={22} strokeWidth={2.8} />
                  </p>
                </div>
                <div className="rounded-2xl bg-emerald-50 border-2 border-emerald-100 p-4">
                  <p className="text-xs font-black uppercase text-slate-400">{t("games.correct")}</p>
                  <p data-testid="game-profile-correct" className="text-3xl font-black text-emerald-500">{profile?.correctAnswers || 0}</p>
                </div>
                <div className="rounded-2xl bg-yellow-50 border-2 border-yellow-100 p-4">
                  <p className="text-xs font-black uppercase text-slate-400">{t("games.badges")}</p>
                  <p data-testid="game-profile-badges-count" className="text-3xl font-black text-yellow-500">{unlockedCount}</p>
                </div>
              </div>
            </section>

            <section className="card-tactile p-5" data-testid="game-badges-card">
              <div className="flex items-center gap-2 mb-4">
                <Medal size={22} strokeWidth={2.8} className="text-sky-500" />
                <h2 className="text-2xl font-black text-slate-800">{t("games.achievements")}</h2>
              </div>
              <div className="space-y-3">
                {profile?.badges?.map((badge) => (
                  <div
                    key={badge.id}
                    data-testid={`game-badge-${badge.id}`}
                    className={`flex items-center gap-3 rounded-2xl border-2 p-3 ${badge.unlocked ? "bg-white border-slate-200" : "bg-slate-50 border-slate-200 opacity-75"}`}
                  >
                    <div className="w-11 h-11 rounded-2xl bg-slate-100 flex items-center justify-center text-xl flex-shrink-0">
                      {badge.unlocked ? badge.icon : <Lock size={18} strokeWidth={2.8} className="text-slate-400" />}
                    </div>
                    <div className="min-w-0">
                      <p className="font-black text-slate-800 truncate">{badge.title}</p>
                      <p className="text-xs font-semibold text-slate-500 leading-snug">{badge.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </aside>
        </div>
      )}
    </div>
  );
}

function QuizCard({ mode, testPrefix, quiz, selectedOptionId, result, submitting, onSelect, onSubmit, title, kicker, icon, gradient, t, visual }) {
  return (
    <section className="card-tactile overflow-hidden animate-slide-up" data-testid={`${testPrefix}-card`}>
      <div className={`bg-gradient-to-r ${gradient} p-5 text-white`}>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            {icon}
            <div className="min-w-0">
              <p data-testid={`${testPrefix}-kicker`} className="text-xs font-black uppercase tracking-widest text-white/80">
                {kicker}
              </p>
              <h2 data-testid={`${testPrefix}-title`} className="text-2xl sm:text-3xl font-black leading-tight truncate">
                {title}
              </h2>
            </div>
          </div>
          {quiz?.league?.emblem && (
            <img data-testid={`${testPrefix}-league-emblem`} src={quiz.league.emblem} alt="" className="w-14 h-14 object-contain bg-white/90 rounded-2xl p-2" />
          )}
        </div>
      </div>

      <div className="p-5 sm:p-6">
        {visual && (
          <div className="mb-5 flex justify-center">
            <div className="w-36 h-36 rounded-[2rem] bg-white border-2 border-slate-200 shadow-[0_6px_0_#CBD5E1] flex items-center justify-center p-5">
              <img data-testid={`${testPrefix}-crest-image`} src={visual} alt="" className="max-w-full max-h-full object-contain" />
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-5">
          {quiz?.hints?.map((hint, index) => (
            <span
              key={hint}
              data-testid={`${testPrefix}-hint-${index}`}
              className="inline-flex items-center gap-1.5 rounded-full border-2 border-slate-200 bg-slate-50 px-3 py-2 text-sm font-bold text-slate-600"
            >
              <Sparkles size={14} strokeWidth={2.8} className="text-yellow-500" />
              {hint}
            </span>
          ))}
        </div>

        <p data-testid={`${testPrefix}-question`} className="text-xl sm:text-2xl font-black text-slate-800 leading-snug mb-5">
          {quiz?.question}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5" data-testid={`${testPrefix}-options`}>
          {quiz?.options?.map((option, index) => {
            const selected = selectedOptionId === option.id;
            const isCorrect = result?.correctOptionId === option.id;
            const isWrongChoice = result && selected && !isCorrect;
            return (
              <button
                key={option.id}
                data-testid={`${testPrefix}-option-${index}`}
                onClick={() => onSelect(mode, option.id)}
                disabled={!!result}
                className={`min-h-[58px] rounded-2xl border-2 px-4 py-3 text-left font-black transition-all duration-200 flex items-center justify-between gap-3 ${
                  isCorrect
                    ? "bg-emerald-100 border-emerald-400 text-emerald-700"
                    : isWrongChoice
                      ? "bg-red-100 border-red-300 text-red-700"
                      : selected
                        ? "bg-sky-100 border-sky-400 text-sky-700 shadow-[0_4px_0_#38BDF8] -translate-y-0.5"
                        : "bg-white border-slate-300 text-slate-700 hover:bg-sky-50 hover:border-sky-300"
                }`}
              >
                <span className="truncate">{option.label}</span>
                {isCorrect && <CheckCircle2 size={20} strokeWidth={3} className="flex-shrink-0" />}
                {isWrongChoice && <XCircle size={20} strokeWidth={3} className="flex-shrink-0" />}
              </button>
            );
          })}
        </div>

        {result && (
          <div
            data-testid={`${testPrefix}-result-message`}
            className={`rounded-2xl border-2 p-4 mb-5 font-bold ${result.isCorrect ? "bg-emerald-50 border-emerald-300 text-emerald-700" : "bg-yellow-50 border-yellow-300 text-yellow-700"}`}
          >
            {result.explanation}
          </div>
        )}

        <Button
          data-testid={`${testPrefix}-submit-button`}
          onClick={() => onSubmit(mode)}
          disabled={!selectedOptionId || !!result || submitting}
          className="btn-chunky w-full min-h-[52px] bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-black rounded-full text-base"
        >
          {submitting ? t("games.checking") : result ? t("games.doneToday") : t("games.submit")}
        </Button>
      </div>
    </section>
  );
}