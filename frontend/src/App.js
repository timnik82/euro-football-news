import "@/App.css";
import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { LanguageProvider, useLanguage } from "@/contexts/LanguageContext";
import AuthCallback from "@/components/AuthCallback";
import Navigation from "@/components/Navigation";
import LoginPage from "@/pages/LoginPage";
import HomePage from "@/pages/HomePage";
import LandingPage from "@/pages/LandingPage";
import LeagueDetail, { LeaguesList } from "@/pages/LeaguePage";
import FavoritesPage from "@/pages/FavoritesPage";
import TeamPage from "@/pages/TeamPage";
import { Toaster } from "@/components/ui/sonner";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { WifiOff } from "lucide-react";

function OfflineBanner() {
  const isOnline = useOnlineStatus();
  const { t } = useLanguage();
  if (isOnline) return null;
  return (
    <div
      data-testid="offline-banner"
      className="fixed top-0 left-0 right-0 z-[100] bg-amber-400 text-amber-900 px-4 py-2.5 flex items-center justify-center gap-2 font-bold text-sm shadow-md animate-slide-up"
    >
      <WifiOff size={16} strokeWidth={3} />
      <span>{t("offline")}</span>
    </div>
  );
}

function AppLayout() {
  const { user, loading } = useAuth();
  const { t } = useLanguage();
  const isOnline = useOnlineStatus();
  const location = useLocation();
  const isAuthCallback = location.hash?.includes("session_id=");
  const [skipLanding, setSkipLanding] = useState(
    () => sessionStorage.getItem("gk_skip_landing") === "1"
  );
  const enterApp = () => {
    sessionStorage.setItem("gk_skip_landing", "1");
    setSkipLanding(true);
  };
  const showLanding = !loading && !user && !skipLanding;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F0F9FF]">
        <div className="text-center animate-bounce-in">
          <h1 className="text-4xl font-black text-sky-500 mb-2">{t("loading")}</h1>
          <p className="text-slate-500 font-semibold">{t("loadingSub")}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-[#F0F9FF] pb-24 ${!isOnline ? 'pt-10' : ''}`}>
      <OfflineBanner />
      {isAuthCallback ? (
        <AuthCallback />
      ) : (
        <>
          <Routes>
            <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
            <Route
              path="/"
              element={showLanding ? <LandingPage onEnter={enterApp} /> : <HomePage />}
            />
            <Route path="/leagues" element={<LeaguesList />} />
            <Route path="/league/:code" element={<LeagueDetail />} />
            <Route path="/team/:id" element={<TeamPage />} />
            <Route path="/favorites" element={user ? <FavoritesPage /> : <Navigate to="/login" />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
          {!(showLanding && location.pathname === "/") && <Navigation />}
        </>
      )}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>
          <AppLayout />
          <Toaster position="top-center" richColors />
        </AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
}

export default App;
