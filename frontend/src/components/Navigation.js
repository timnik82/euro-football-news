import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { Home, Trophy, Heart, User, LogIn } from "lucide-react";
import { toast } from "sonner";

const navItems = [
  { path: "/", icon: Home, tKey: "nav.home" },
  { path: "/leagues", icon: Trophy, tKey: "nav.leagues" },
  { path: "/favorites", icon: Heart, tKey: "nav.favorites" },
];

export default function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { t } = useLanguage();

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
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-slate-200 px-4 py-2 z-50" data-testid="bottom-navigation">
      <div className="flex items-center justify-around max-w-lg mx-auto">
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <button
              key={item.path}
              data-testid={`nav-${item.tKey.split(".")[1]}`}
              onClick={() => {
                if (item.path === "/favorites" && !user) {
                  toast.info(t("nav.login") + "!");
                  navigate("/login");
                  return;
                }
                navigate(item.path);
              }}
              className={`flex flex-col items-center gap-0.5 px-4 py-2 rounded-2xl transition-all duration-200 min-w-[64px] min-h-[48px] ${
                active ? "bg-sky-100 text-sky-500" : "text-slate-400 hover:text-slate-600"
              }`}
            >
              <item.icon size={22} strokeWidth={active ? 3 : 2.5} />
              <span className="text-[11px] font-bold">{t(item.tKey)}</span>
            </button>
          );
        })}
        <button
          data-testid="nav-profile"
          onClick={handleProfileClick}
          className="flex flex-col items-center gap-0.5 px-4 py-2 rounded-2xl transition-all duration-200 min-w-[64px] min-h-[48px] text-slate-400 hover:text-slate-600"
        >
          {user ? <User size={22} strokeWidth={2.5} /> : <LogIn size={22} strokeWidth={2.5} />}
          <span className="text-[11px] font-bold">
            {user ? user.name?.split(" ")[0] || t("nav.logout") : t("nav.login")}
          </span>
        </button>
      </div>
    </nav>
  );
}
