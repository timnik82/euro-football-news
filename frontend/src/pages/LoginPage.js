import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useNavigate } from "react-router-dom";
import { BrandHeading } from "@/components/BrandHeading";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LogIn, UserPlus } from "lucide-react";

const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" aria-hidden="true">
    <path fill="#EA4335" d="M12 10.2v3.9h5.4c-.2 1.2-.9 2.2-1.9 2.9l3 2.3c1.8-1.6 2.8-4 2.8-6.8 0-.6-.1-1.2-.2-1.8H12z" />
    <path fill="#34A853" d="M12 21c2.6 0 4.8-.9 6.4-2.5l-3-2.3c-.8.5-2 .9-3.4.9-2.6 0-4.7-1.7-5.5-4.1l-3.1 2.4C5 18.6 8.2 21 12 21z" />
    <path fill="#4A90E2" d="M6.5 13c-.2-.5-.3-1-.3-1.6s.1-1.1.3-1.6L3.4 7.4C2.8 8.6 2.5 9.8 2.5 11.4s.3 2.8.9 4l3.1-2.4z" />
    <path fill="#FBBC05" d="M12 5.8c1.4 0 2.6.5 3.6 1.4l2.7-2.7C16.8 3.1 14.6 2 12 2 8.2 2 5 4.4 3.4 7.4l3.1 2.4C7.3 7.5 9.4 5.8 12 5.8z" />
  </svg>
);

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login, register, signInWithGoogle } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    const result = isRegister
      ? await register(name, email, password)
      : await login(email, password);
    setSubmitting(false);
    if (result.success) {
      navigate("/");
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url('https://images.unsplash.com/photo-1542652420-d071027a88bb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwyfHxldXJvcGVhbiUyMGZvb3RiYWxsJTIwc3RhZGl1bXxlbnwwfHx8fDE3NzU1OTY2MDN8MA&ixlib=rb-4.1.0&q=85')" }}
      />
      <div className="absolute inset-0 bg-blue-900/70" />

      <div className="relative z-10 w-full max-w-md animate-bounce-in">
        <div className="card-tactile p-8">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <BrandHeading label="Goal Kick" size="md" testId="login-brand-heading" />
            </div>
            <h1 className="text-3xl font-black text-slate-800 tracking-tight">
              {isRegister ? t("login.joinClub") : t("login.welcomeBack")}
            </h1>
            <p className="text-slate-500 font-semibold mt-1">
              {isRegister ? t("login.registerSub") : t("login.loginSub")}
            </p>
          </div>

          <div className="space-y-4 mb-6">
            <Button
              type="button"
              variant="outline"
              data-testid="google-auth-button"
              onClick={signInWithGoogle}
              className="w-full h-14 rounded-2xl border-2 border-slate-300 bg-white hover:bg-slate-50 text-slate-800 text-base font-bold"
            >
              <span className="flex items-center gap-3">
                <GoogleIcon />
                {t("login.googleBtn")}
              </span>
            </Button>
            <div className="flex items-center gap-3" data-testid="auth-method-divider">
              <div className="h-px flex-1 bg-slate-200" />
              <span className="text-xs font-bold uppercase tracking-[0.24em] text-slate-400">
                {t("login.googleDivider")}
              </span>
              <div className="h-px flex-1 bg-slate-200" />
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {isRegister && (
              <div className="space-y-2">
                <Label htmlFor="name" className="font-bold text-slate-700">{t("login.name")}</Label>
                <Input
                  data-testid="register-name-input"
                  id="name" type="text" placeholder={t("login.namePlaceholder")}
                  value={name} onChange={(e) => setName(e.target.value)} required
                  className="h-12 rounded-2xl border-2 border-slate-300 text-base font-semibold focus:border-sky-400"
                />
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email" className="font-bold text-slate-700">{t("login.email")}</Label>
              <Input
                data-testid="login-email-input"
                id="email" type="email" placeholder={t("login.emailPlaceholder")}
                value={email} onChange={(e) => setEmail(e.target.value)} required
                className="h-12 rounded-2xl border-2 border-slate-300 text-base font-semibold focus:border-sky-400"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="font-bold text-slate-700">{t("login.password")}</Label>
              <Input
                data-testid="login-password-input"
                id="password" type="password" placeholder={t("login.passwordPlaceholder")}
                value={password} onChange={(e) => setPassword(e.target.value)} required minLength={4}
                className="h-12 rounded-2xl border-2 border-slate-300 text-base font-semibold focus:border-sky-400"
              />
            </div>

            {error && (
              <div data-testid="auth-error-message" className="bg-red-50 border-2 border-red-200 rounded-2xl p-3 text-red-600 font-semibold text-sm text-center">
                {error}
              </div>
            )}

            <Button
              data-testid="auth-submit-button" type="submit" disabled={submitting}
              className="w-full h-14 btn-chunky bg-sky-500 hover:bg-sky-600 text-white text-lg font-bold"
            >
              {submitting ? "..." : isRegister ? (
                <span className="flex items-center gap-2"><UserPlus size={20} strokeWidth={2.5} /> {t("login.registerBtn")}</span>
              ) : (
                <span className="flex items-center gap-2"><LogIn size={20} strokeWidth={2.5} /> {t("login.loginBtn")}</span>
              )}
            </Button>
          </form>

          <div className="text-center mt-6">
            <button
              data-testid="auth-toggle-button" type="button"
              onClick={() => { setIsRegister(!isRegister); setError(""); }}
              className="text-sky-500 font-bold hover:text-sky-600 transition-colors"
            >
              {isRegister ? t("login.toggleLogin") : t("login.toggleRegister")}
            </button>
          </div>
          <div className="text-center mt-3">
            <button
              data-testid="skip-login-button" type="button" onClick={() => navigate("/")}
              className="text-slate-400 font-semibold hover:text-slate-600 transition-colors text-sm"
            >
              {t("login.skip")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
