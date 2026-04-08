import { createContext, useContext, useState, useCallback } from "react";
import { getTranslation, DATE_LOCALES } from "@/i18n/translations";

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    try { return localStorage.getItem("goal-kick-lang") || "en"; }
    catch { return "en"; }
  });

  const switchLanguage = useCallback((lang) => {
    setLanguage(lang);
    try { localStorage.setItem("goal-kick-lang", lang); } catch {}
  }, []);

  const t = useCallback((key) => getTranslation(language, key), [language]);

  const dateLocale = DATE_LOCALES[language] || "en-GB";

  return (
    <LanguageContext.Provider value={{ language, switchLanguage, t, dateLocale }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
