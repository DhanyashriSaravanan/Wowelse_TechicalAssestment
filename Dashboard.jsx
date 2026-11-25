import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { apiRequest } from "../api";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function loadProfile() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const profile = await apiRequest("/api/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(profile);
      } catch {
        localStorage.removeItem("access_token");
        setError("Your session has expired. Please log in again.");
        navigate("/login");
      }
    }

    loadProfile();
  }, [navigate]);

  return (
    <>
      <Navbar />
      <main className="dashboard-card">
        <h1>Dashboard</h1>
        {user ? (
          <>
            <p className="welcome">Welcome, {user.name || user.email}!</p>
            <div className="profile-row"><strong>Email:</strong><span>{user.email}</span></div>
            <div className="profile-row"><strong>Username:</strong><span>{user.username || "Google account"}</span></div>
            <div className="profile-row"><strong>Login method:</strong><span>{user.auth_provider === "google" ? "Google" : "Email and password"}</span></div>
            <p className="success-note">You are successfully logged in.</p>
          </>
        ) : <p>{error || "Loading your profile..."}</p>}
      </main>
    </>
  );
}
