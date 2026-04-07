import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LogIn, UserPlus, Trophy } from "lucide-react";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login, register } = useAuth();
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
      {/* Stadium background */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url('https://images.unsplash.com/photo-1542652420-d071027a88bb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwyfHxldXJvcGVhbiUyMGZvb3RiYWxsJTIwc3RhZGl1bXxlbnwwfHx8fDE3NzU1OTY2MDN8MA&ixlib=rb-4.1.0&q=85')" }}
      />
      <div className="absolute inset-0 bg-blue-900/70" />

      {/* Login card */}
      <div className="relative z-10 w-full max-w-md animate-bounce-in">
        <div className="card-tactile p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-sky-100 mb-4">
              <Trophy size={32} strokeWidth={2.5} className="text-sky-500" />
            </div>
            <h1 className="text-3xl font-black text-slate-800 tracking-tight">
              {isRegister ? "Join the Club!" : "Welcome Back!"}
            </h1>
            <p className="text-slate-500 font-semibold mt-1">
              {isRegister ? "Create your account to save favorites" : "Log in to see your favorites"}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {isRegister && (
              <div className="space-y-2">
                <Label htmlFor="name" className="font-bold text-slate-700">Your Name</Label>
                <Input
                  data-testid="register-name-input"
                  id="name"
                  type="text"
                  placeholder="e.g. Alex"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="h-12 rounded-2xl border-2 border-slate-300 text-base font-semibold focus:border-sky-400"
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="font-bold text-slate-700">Email</Label>
              <Input
                data-testid="login-email-input"
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 rounded-2xl border-2 border-slate-300 text-base font-semibold focus:border-sky-400"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="font-bold text-slate-700">Password</Label>
              <Input
                data-testid="login-password-input"
                id="password"
                type="password"
                placeholder="Your secret password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={4}
                className="h-12 rounded-2xl border-2 border-slate-300 text-base font-semibold focus:border-sky-400"
              />
            </div>

            {error && (
              <div data-testid="auth-error-message" className="bg-red-50 border-2 border-red-200 rounded-2xl p-3 text-red-600 font-semibold text-sm text-center">
                {error}
              </div>
            )}

            <Button
              data-testid="auth-submit-button"
              type="submit"
              disabled={submitting}
              className="w-full h-14 btn-chunky bg-sky-500 hover:bg-sky-600 text-white text-lg font-bold"
            >
              {submitting ? (
                "Loading..."
              ) : isRegister ? (
                <span className="flex items-center gap-2"><UserPlus size={20} strokeWidth={2.5} /> Create Account</span>
              ) : (
                <span className="flex items-center gap-2"><LogIn size={20} strokeWidth={2.5} /> Log In</span>
              )}
            </Button>
          </form>

          {/* Toggle */}
          <div className="text-center mt-6">
            <button
              data-testid="auth-toggle-button"
              type="button"
              onClick={() => { setIsRegister(!isRegister); setError(""); }}
              className="text-sky-500 font-bold hover:text-sky-600 transition-colors"
            >
              {isRegister ? "Already have an account? Log in" : "New here? Create an account"}
            </button>
          </div>

          {/* Skip */}
          <div className="text-center mt-3">
            <button
              data-testid="skip-login-button"
              type="button"
              onClick={() => navigate("/")}
              className="text-slate-400 font-semibold hover:text-slate-600 transition-colors text-sm"
            >
              Skip for now - browse matches
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
