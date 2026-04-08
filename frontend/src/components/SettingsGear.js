import { useLanguage } from "@/contexts/LanguageContext";
import { LANGUAGES } from "@/i18n/translations";
import { Settings, Check } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

export default function SettingsGear() {
  const { language, switchLanguage, t } = useLanguage();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          data-testid="settings-gear-button"
          className="fixed top-4 right-4 z-50 w-10 h-10 rounded-full bg-white/80 backdrop-blur border-2 border-slate-200 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:border-slate-300 transition-all duration-200 hover:rotate-45"
        >
          <Settings size={18} strokeWidth={2.5} />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="w-48 rounded-2xl border-2 border-slate-200 shadow-lg p-1"
      >
        <DropdownMenuLabel className="text-xs font-bold uppercase tracking-widest text-slate-400 px-3 py-2">
          {t("settings.language")}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {LANGUAGES.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            data-testid={`lang-option-${lang.code}`}
            onClick={() => switchLanguage(lang.code)}
            className="rounded-xl px-3 py-2.5 font-semibold cursor-pointer flex items-center gap-3 min-h-[44px]"
          >
            <span className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-xs font-black text-slate-600">
              {lang.short}
            </span>
            <span className="flex-1">{lang.label}</span>
            {language === lang.code && (
              <Check size={16} strokeWidth={3} className="text-sky-500" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
