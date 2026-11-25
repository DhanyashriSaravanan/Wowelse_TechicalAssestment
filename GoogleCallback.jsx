import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiRequest } from "../api";

export default function GoogleCallback() {
  const [params] = useSearchParams();
  const [message, setMessage] = useState("Completing Google sign-in...");
  const navigate = useNavigate();

  useEffect(() => {
    async function finishLogin() {
      const code = params.get("code");

      if (!code) {
        setMessage("Google sign-in code was not found.");
        setTimeout(() => navigate("/login"), 1500);
        return;
      }

      try {
        const result = await apiRequest("/api/auth/google/exchange", {
          method: "POST",
          body: JSON.stringify({ code }),
        });
        localStorage.setItem("access_token", result.access_token);
        navigate("/dashboard", { replace: true });
      } catch (error) {
        setMessage(error.message);
        setTimeout(() => navigate("/login"), 1800);
      }
    }

    finishLogin();
  }, [params, navigate]);

  return <main className="auth-card"><p>{message}</p></main>;
}
