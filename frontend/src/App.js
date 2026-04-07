import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import Navigation from "@/components/Navigation";
import LoginPage from "@/pages/LoginPage";
import HomePage from "@/pages/HomePage";
import LeagueDetail, { LeaguesList } from "@/pages/LeaguePage";
import FavoritesPage from "@/pages/FavoritesPage";
import { Toaster } from "@/components/ui/sonner";

function AppLayout() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F0F9FF]">
        <div className="text-center animate-bounce-in">
          <h1 className="text-4xl font-black text-sky-500 mb-2">Loading...</h1>
          <p className="text-slate-500 font-semibold">Getting the latest scores</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F0F9FF] pb-24">
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/leagues" element={<LeaguesList />} />
        <Route path="/league/:code" element={<LeagueDetail />} />
        <Route path="/favorites" element={user ? <FavoritesPage /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <Navigation />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppLayout />
        <Toaster position="top-center" richColors />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
