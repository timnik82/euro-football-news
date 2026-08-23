import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export default function AuthCallback() {
  const location = useLocation();
  const navigate = useNavigate();
  const { exchangeGoogleSession } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const params = new URLSearchParams(location.hash.replace(/^#/, ""));
    const sessionId = params.get("session_id");

    if (!sessionId) {
      navigate("/login", { replace: true });
      return;
    }

    const completeGoogleSignIn = async () => {
      const result = await exchangeGoogleSession(sessionId);
      if (result.success) {
        navigate("/", { replace: true });
        return;
      }
      toast.error(result.error || "Google sign-in failed");
      navigate("/login", { replace: true });
    };

    completeGoogleSignIn();
  }, [exchangeGoogleSession, location.hash, navigate]);

  return <div data-testid="google-auth-callback" className="sr-only">Completing Google sign in</div>;
}