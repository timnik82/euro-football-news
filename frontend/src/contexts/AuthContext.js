import { createContext, useContext, useState, useEffect, useCallback } from "react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const AuthContext = createContext(null);

function formatError(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/auth/me`, { withCredentials: true });
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // CRITICAL: If returning from OAuth callback, skip the /me check.
    // AuthCallback will exchange the session_id and establish the session first.
    if (window.location.hash?.includes("session_id=")) {
      setLoading(false);
      return;
    }
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      const { data } = await axios.post(`${API}/auth/login`, { email, password }, { withCredentials: true });
      setUser(data);
      return { success: true };
    } catch (e) {
      return { success: false, error: formatError(e.response?.data?.detail) || e.message };
    }
  };

  const register = async (name, email, password) => {
    try {
      const { data } = await axios.post(`${API}/auth/register`, { name, email, password }, { withCredentials: true });
      setUser(data);
      return { success: true };
    } catch (e) {
      return { success: false, error: formatError(e.response?.data?.detail) || e.message };
    }
  };

  const signInWithGoogle = useCallback(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + "/";
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  }, []);

  const exchangeGoogleSession = useCallback(async (sessionId) => {
    try {
      const { data } = await axios.post(
        `${API}/auth/google/session`,
        { session_id: sessionId },
        { withCredentials: true },
      );
      setUser(data);
      return { success: true, user: data };
    } catch (e) {
      return { success: false, error: formatError(e.response?.data?.detail) || e.message };
    }
  }, []);

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch { /* ignore */ }
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, signInWithGoogle, exchangeGoogleSession, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
