import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Heart, Trash2, Trophy, Users } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function FavoritesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const { data } = await axios.get(`${API}/favorites`, { withCredentials: true });
      setFavorites(data);
    } catch {
      toast.error("Could not load favorites");
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (fav) => {
    try {
      await axios.post(
        `${API}/favorites`,
        { type: fav.type, item_id: fav.item_id, name: fav.name, crest: fav.crest || "" },
        { withCredentials: true }
      );
      setFavorites(favorites.filter((f) => !(f.type === fav.type && f.item_id === fav.item_id)));
      toast.success("Removed from favorites");
    } catch {
      toast.error("Could not remove favorite");
    }
  };

  const leagueFavs = favorites.filter((f) => f.type === "league");
  const teamFavs = favorites.filter((f) => f.type === "team");

  return (
    <div className="max-w-5xl mx-auto px-4 pt-6">
      <div className="flex items-center gap-3 mb-6 animate-slide-up">
        <Heart size={28} strokeWidth={2.5} className="text-red-400 fill-red-400" />
        <h1 className="text-4xl sm:text-5xl font-black text-slate-800 tracking-tight">
          My Favorites
        </h1>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card-tactile h-20 animate-pulse" />
          ))}
        </div>
      ) : favorites.length === 0 ? (
        <div className="card-tactile p-10 text-center animate-bounce-in">
          <Heart size={48} strokeWidth={2} className="text-slate-300 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-slate-700 mb-2">No favorites yet</h3>
          <p className="text-slate-500 font-semibold mb-4">
            Browse leagues and tap the heart to save your favorite teams and competitions!
          </p>
          <Button
            data-testid="browse-leagues-btn"
            onClick={() => navigate("/leagues")}
            className="btn-chunky bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-full px-8 py-3"
          >
            Browse Leagues
          </Button>
        </div>
      ) : (
        <>
          {/* League Favorites */}
          {leagueFavs.length > 0 && (
            <section className="mb-8 animate-slide-up">
              <div className="flex items-center gap-2 mb-4">
                <Trophy size={20} strokeWidth={2.5} className="text-yellow-500" />
                <h2 className="text-xl font-bold text-slate-800">Leagues</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {leagueFavs.map((fav) => (
                  <div key={`${fav.type}-${fav.item_id}`} className="card-tactile p-5 flex items-center gap-4">
                    <button
                      data-testid={`fav-league-go-${fav.item_id}`}
                      onClick={() => navigate(`/league/${fav.item_id}`)}
                      className="flex-1 text-left"
                    >
                      <div className="font-bold text-slate-800 text-lg">{fav.name}</div>
                    </button>
                    <button
                      data-testid={`remove-fav-${fav.type}-${fav.item_id}`}
                      onClick={() => removeFavorite(fav)}
                      className="w-10 h-10 rounded-full flex items-center justify-center bg-red-50 hover:bg-red-100 transition-colors"
                    >
                      <Trash2 size={16} strokeWidth={2.5} className="text-red-400" />
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Team Favorites */}
          {teamFavs.length > 0 && (
            <section className="animate-slide-up" style={{ animationDelay: "0.05s" }}>
              <div className="flex items-center gap-2 mb-4">
                <Users size={20} strokeWidth={2.5} className="text-sky-500" />
                <h2 className="text-xl font-bold text-slate-800">Teams</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {teamFavs.map((fav) => (
                  <div key={`${fav.type}-${fav.item_id}`} className="card-tactile p-5 flex items-center gap-4">
                    {fav.crest && <img src={fav.crest} alt="" className="w-10 h-10 object-contain flex-shrink-0" />}
                    <button
                      data-testid={`fav-team-go-${fav.item_id}`}
                      onClick={() => fav.league_code ? navigate(`/league/${fav.league_code}`) : null}
                      className="flex-1 text-left"
                    >
                      <div className="font-bold text-slate-800">{fav.name}</div>
                    </button>
                    <button
                      data-testid={`remove-fav-${fav.type}-${fav.item_id}`}
                      onClick={() => removeFavorite(fav)}
                      className="w-10 h-10 rounded-full flex items-center justify-center bg-red-50 hover:bg-red-100 transition-colors"
                    >
                      <Trash2 size={16} strokeWidth={2.5} className="text-red-400" />
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
