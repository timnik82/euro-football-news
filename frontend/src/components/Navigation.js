import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { Home, Trophy, Heart, User, LogIn, Search, LogOut, BadgeCheck } from "lucide-react";
import { toast } from "sonner";
import SearchModal from "@/components/SearchModal";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

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
  const [searchOpen, setSearchOpen] = useState(false);

  if (location.pathname === "/login") return null;

  const handleLogout = async () => {
    await logout();
    toast.success(t("nav.logout"));
    navigate("/");
  };

  const isActive = (path) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  const firstName = user?.name?.split(" ")[0] || t("nav.profile");
  const initials = (user?.name || t("nav.profile"))
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "GK";

  const providerLabel = user?.auth_provider === "google"
    ? t("nav.providerGoogle")
    : user?.auth_provider === "email_google"
      ? t("nav.providerLinked")
      : t("nav.providerEmail");

  return (
    <>
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
                className={`flex flex-col items-center gap-0.5 px-4 py-2 rounded-2xl transition-all duration-200 min-w-[56px] min-h-[48px] ${
                  active ? "bg-sky-100 text-sky-500" : "text-slate-400 hover:text-slate-600"
                }`}
              >
                <item.icon size={22} strokeWidth={active ? 3 : 2.5} />
                <span className="text-[11px] font-bold">{t(item.tKey)}</span>
              </button>
            );
          })}
          {/* Search button */}
          <button
            data-testid="nav-search"
            onClick={() => setSearchOpen(true)}
            className="flex flex-col items-center gap-0.5 px-4 py-2 rounded-2xl transition-all duration-200 min-w-[56px] min-h-[48px] text-slate-400 hover:text-sky-500"
          >
            <Search size={22} strokeWidth={2.5} />
            <span className="text-[11px] font-bold">Search</span>
          </button>
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  data-testid="nav-profile-menu-trigger"
                  className="flex flex-col items-center gap-1 px-3 py-2 rounded-2xl transition-all duration-200 min-w-[72px] min-h-[48px] text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                >
                  <div className="relative">
                    <Avatar className="w-8 h-8 border-2 border-white shadow-sm" data-testid="nav-profile-avatar">
                      <AvatarImage src={user.picture || undefined} alt={user.name || t("nav.profile")} />
                      <AvatarFallback className="bg-sky-100 text-sky-700 text-xs font-black">
                        {initials}
                      </AvatarFallback>
                    </Avatar>
                    <span
                      data-testid="nav-profile-status-dot"
                      className="absolute -right-0.5 -bottom-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-white"
                    />
                  </div>
                  <span className="text-[11px] font-bold truncate max-w-[64px]">{firstName}</span>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                side="top"
                sideOffset={10}
                className="w-64 rounded-2xl border-2 border-slate-200 bg-white p-2 shadow-xl"
                data-testid="nav-profile-menu"
              >
                <DropdownMenuLabel className="p-0">
                  <div className="flex items-center gap-3 rounded-xl bg-sky-50 px-3 py-3" data-testid="nav-profile-menu-header">
                    <Avatar className="w-11 h-11 border-2 border-white shadow-sm">
                      <AvatarImage src={user.picture || undefined} alt={user.name || t("nav.profile")} />
                      <AvatarFallback className="bg-sky-100 text-sky-700 text-sm font-black">
                        {initials}
                      </AvatarFallback>
                    </Avatar>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-black text-slate-800 truncate" data-testid="nav-profile-menu-name">
                        {user.name || t("nav.profile")}
                      </div>
                      <div className="text-xs font-semibold text-slate-500 truncate" data-testid="nav-profile-menu-email">
                        {user.email}
                      </div>
                    </div>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="my-2 bg-slate-200" />
                <div className="px-3 pb-2" data-testid="nav-profile-provider-row">
                  <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700">
                    <BadgeCheck size={14} strokeWidth={2.5} />
                    {providerLabel}
                  </div>
                </div>
                <DropdownMenuItem
                  data-testid="nav-profile-logout-item"
                  onClick={handleLogout}
                  className="rounded-xl px-3 py-3 font-bold text-red-500 focus:bg-red-50 focus:text-red-600 cursor-pointer"
                >
                  <LogOut size={16} strokeWidth={2.5} />
                  {t("nav.logout")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <button
              data-testid="nav-profile"
              onClick={() => navigate("/login")}
              className="flex flex-col items-center gap-0.5 px-4 py-2 rounded-2xl transition-all duration-200 min-w-[56px] min-h-[48px] text-slate-400 hover:text-slate-600"
            >
              <LogIn size={22} strokeWidth={2.5} />
              <span className="text-[11px] font-bold">{t("nav.login")}</span>
            </button>
          )}
        </div>
      </nav>
      <SearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}
