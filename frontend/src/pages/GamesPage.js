import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { useLanguage } from "@/contexts/LanguageContext";
import { BrandHeading } from "@/components/BrandHeading";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, Flame, Gamepad2, Lock, Medal, RotateCcw, Sparkles, Star, Target, Trophy, XCircle } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function GamesPage() {
  const { t, language } = useLanguage();
  const [quiz, setQuiz] = useState(null);
  const [profile, setProfile] = useState(null);
  const [selectedOptionId, setSelectedOptionId] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchGameData();
  }, [language]);

  const fetchGameData = async () => {
    setLoading(true);
    setResult(null);
    setSelectedOptionId("");
    try {
      const [quizRes, profileRes] = await Promise.all([
        axios.get(`${API}/gamification/daily-quiz?lang=${language}`),
        axios.get(`${API}/gamification/profile?lang=${language}`, { withCredentials: true }),
      ]);
      setQuiz(quizRes.data);
      setProfile(profileRes.data);
      const todayAttempt = profileRes.data.recentAttempts?.find((attempt) => attempt.quizId === quizRes.data.quizId);
      if (todayAttempt) {
        setSelectedOptionId(todayAttempt.selectedOptionId);
        setResult({ ...todayAttempt, alreadyAnswered: true, explanation: t("games.alreadyPlayed") });
      }
    } catch (error) {
      toast.error(t("games.loadError"));
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedOptionId || !quiz || result) return;
    setSubmitting(true);
    try {
      const { data } = await axios.post(
        `${API}/gamification/daily-quiz/answer`,
        { quizId: quiz.quizId, selectedOptionId, language },
        { withCredentials: true }
      );
      setResult(data);
      setProfile(data.profile);
      toast.success(data.isCorrect ? t("games.correctToast") : t("games.tryTomorrow"));
    } catch (error) {
      toast.error(t("games.submitError"));
    } finally {
      setSubmitting(false);
    }
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
          <section className="card-tactile overflow-hidden animate-slide-up" data-testid="daily-quiz-card">
            <div className="bg-gradient-to-r from-emerald-400 via-sky-400 to-yellow-300 p-5 text-white">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <Target size={30} strokeWidth={3} className="flex-shrink-0" />
                  <div className="min-w-0">
                    <p data-testid="daily-quiz-kicker" className="text-xs font-black uppercase tracking-widest text-white/80">
                      {t("games.dailyQuiz")}
                    </p>
                    <h2 data-testid="daily-quiz-title" className="text-2xl sm:text-3xl font-black leading-tight truncate">
                      {t("games.guessPlayer")}
                    </h2>
                  </div>
                </div>
                {quiz?.league?.emblem && (
                  <img data-testid="daily-quiz-league-emblem" src={quiz.league.emblem} alt="" className="w-14 h-14 object-contain bg-white/90 rounded-2xl p-2" />
                )}
              </div>
            </div>

            <div className="p-5 sm:p-6">
              <div className="flex flex-wrap gap-2 mb-5">
                {quiz?.hints?.map((hint, index) => (
                  <span
                    key={hint}
                    data-testid={`daily-quiz-hint-${index}`}
                    className="inline-flex items-center gap-1.5 rounded-full border-2 border-slate-200 bg-slate-50 px-3 py-2 text-sm font-bold text-slate-600"
                  >
                    <Sparkles size={14} strokeWidth={2.8} className="text-yellow-500" />
                    {hint}
                  </span>
                ))}
              </div>

              <p data-testid="daily-quiz-question" className="text-xl sm:text-2xl font-black text-slate-800 leading-snug mb-5">
                {quiz?.question}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5" data-testid="daily-quiz-options">
                {quiz?.options?.map((option, index) => {
                  const selected = selectedOptionId === option.id;
                  const isCorrect = result?.correctOptionId === option.id;
                  const isWrongChoice = result && selected && !isCorrect;
                  return (
                    <button
                      key={option.id}
                      data-testid={`daily-quiz-option-${index}`}
                      onClick={() => !result && setSelectedOptionId(option.id)}
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
                  data-testid="daily-quiz-result-message"
                  className={`rounded-2xl border-2 p-4 mb-5 font-bold ${result.isCorrect ? "bg-emerald-50 border-emerald-300 text-emerald-700" : "bg-yellow-50 border-yellow-300 text-yellow-700"}`}
                >
                  {result.explanation}
                </div>
              )}

              <Button
                data-testid="daily-quiz-submit-button"
                onClick={submitAnswer}
                disabled={!selectedOptionId || !!result || submitting}
                className="btn-chunky w-full min-h-[52px] bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-black rounded-full text-base"
              >
                {submitting ? t("games.checking") : result ? t("games.doneToday") : t("games.submit")}
              </Button>
            </div>
          </section>

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