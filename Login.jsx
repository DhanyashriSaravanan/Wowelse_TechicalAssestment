import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { apiRequest, API_URL } from "../api";

export default function Login() {
  const [form, setForm] = useState({ username_or_email: "", password: "" });
  const [message, setMessage] = useState("");
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    try {
      const result = await apiRequest("/api/login", {
        method: "POST",
        body: JSON.stringify(form),
      });

      localStorage.setItem("access_token", result.access_token);
      navigate("/dashboard");
    } catch (error) {
      setMessage(error.message);
    }
  }

  const googleError = searchParams.get("error");

  return (
    <main className="auth-card">
      <h1>Welcome back</h1>
      <p className="subtitle">Log in to continue.</p>

      {googleError && (
        <p className="message error">
          Google sign-in could not be completed: {googleError.replaceAll("_", " ")}.
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <label htmlFor="username_or_email">Username or email</label>
        <input id="username_or_email" value={form.username_or_email}
          onChange={event => setForm({ ...form, username_or_email: event.target.value })}
          required />

        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={form.password}
          onChange={event => setForm({ ...form, password: event.target.value })}
          required />

        <button type="submit">Log in</button>
      </form>

      {message && <p className="message error">{message}</p>}

      <div className="separator"><span>OR</span></div>
      <button className="google-button"
        onClick={() => window.location.href = `${API_URL}/api/auth/google/login`}>
        <span className="google-mark">G</span> Login with Google
      </button>

      <p className="bottom-text">
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </main>
  );
}
