import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest, API_URL } from "../api";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  function handleChange(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

    if (form.password !== form.confirm_password) {
      setIsError(true);
      setMessage("Passwords do not match");
      return;
    }

    try {
      await apiRequest("/api/register", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setMessage("Registration successful. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1000);
    } catch (error) {
      setIsError(true);
      setMessage(error.message);
    }
  }

  return (
    <main className="auth-card">
      <h1>Create your account</h1>
      <p className="subtitle">Enter your details to get started.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input id="username" name="username" value={form.username}
          onChange={handleChange} minLength="3" required />

        <label htmlFor="email">Email address</label>
        <input id="email" name="email" type="email" value={form.email}
          onChange={handleChange} required />

        <label htmlFor="password">Password</label>
        <input id="password" name="password" type="password" value={form.password}
          onChange={handleChange} minLength="8" required />

        <label htmlFor="confirm_password">Confirm password</label>
        <input id="confirm_password" name="confirm_password" type="password"
          value={form.confirm_password} onChange={handleChange} required />

        <button type="submit">Create account</button>
      </form>

      {message && <p className={isError ? "message error" : "message success"}>{message}</p>}

      <div className="separator"><span>OR</span></div>
      <button className="google-button"
        onClick={() => window.location.href = `${API_URL}/api/auth/google/login`}>
        <span className="google-mark">G</span> Sign up with Google
      </button>

      <p className="bottom-text">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </main>
  );
}
