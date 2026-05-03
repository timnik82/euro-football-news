import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { Home, Trophy, Heart, User, LogIn, Search, Gamepad2 } from "lucide-react";
import { toast } from "sonner";
import SearchModal from "@/components/SearchModal";

const navItems = [
  { path: "/", icon: Home, tKey: "nav.home" },
  { path: "/leagues", icon: Trophy, tKey: "nav.leagues" },
  { path: "/games", icon: Gamepad2, tKey: "nav.games" },
  { path: "/favorites", icon: Heart, tKey: "nav.favorites" },
];

export default function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const [searchOpen, setSearchOpen] = useState(false);

  if (location.pathname === "/login") return null;

  const handleProfileClick = async () => {
    if (user) {
      await logout();
      toast.success(t("nav.logout"));
      navigate("/");
    } else {
      navigate("/login");
    }
  };

  const isActive = (path) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-slate-200 px-2 py-2 z-50" data-testid="bottom-navigation">
        <div className="flex items-center justify-around max-w-xl mx-auto gap-1">
          {navItems.map((item) => {
            const active = isActive(item.path);
            return (
              <button
                key={item.path}
                data-testid={`nav-${item.tKey.split(".")[1]}`}
                onClick={() => {
                  if ((item.path === "/favorites" || item.path === "/games") && !user) {
                    toast.info(t("nav.login") + "!");
                    navigate("/login");
                    return;
                  }
                  navigate(item.path);
                }}
                className={`flex flex-col items-center gap-0.5 px-2 sm:px-4 py-2 rounded-2xl transition-all duration-200 min-w-[46px] sm:min-w-[56px] min-h-[48px] ${
                  active ? "bg-sky-100 text-sky-500" : "text-slate-400 hover:text-slate-600"
                }`}
              >
                <item.icon size={21} strokeWidth={active ? 3 : 2.5} />
                <span className="text-[10px] sm:text-[11px] font-bold leading-tight">{t(item.tKey)}</span>
              </button>
            );
          })}
          {/* Search button */}
          <button
            data-testid="nav-search"
            onClick={() => setSearchOpen(true)}
            className="flex flex-col items-center gap-0.5 px-2 sm:px-4 py-2 rounded-2xl transition-all duration-200 min-w-[46px] sm:min-w-[56px] min-h-[48px] text-slate-400 hover:text-sky-500"
          >
            <Search size={21} strokeWidth={2.5} />
            <span className="text-[10px] sm:text-[11px] font-bold leading-tight">{t("nav.search")}</span>
          </button>
          <button
            data-testid="nav-profile"
            onClick={handleProfileClick}
            className="flex flex-col items-center gap-0.5 px-2 sm:px-4 py-2 rounded-2xl transition-all duration-200 min-w-[46px] sm:min-w-[56px] min-h-[48px] text-slate-400 hover:text-slate-600"
          >
            {user ? <User size={21} strokeWidth={2.5} /> : <LogIn size={21} strokeWidth={2.5} />}
            <span className="text-[10px] sm:text-[11px] font-bold leading-tight max-w-[52px] truncate">
              {user ? user.name?.split(" ")[0] || t("nav.logout") : t("nav.login")}
            </span>
          </button>
        </div>
      </nav>
      <SearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}
