import { useState } from "react";
import { useAuth } from "./AuthContext";
import { useToast } from "../components/Toast";
import { apiFetch } from "../api/api";

export default function AuthForm({ onClose }) {
  const { login } = useAuth();
  const toast = useToast();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    const endpoint = mode === "login" ? "/api/auth/login" : "/api/auth/register";

    try {
      const res = await apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (res?.access_token) {
        login(res.access_token);
        toast.success("Logged in successfully!");
        onClose?.();
      } else {
        // Registration success
        toast.success("Account created! You can now log in.");
        setMode("login");
        setPassword("");
      }
    } catch (err) {
      toast.error(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="authBox">
      <h3>{mode === "login" ? "Welcome Back" : "Create Account"}</h3>

      <input
        type="email"
        placeholder="Email address"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
        autoFocus
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
        minLength={8}
      />

      <button type="submit" className="primaryBtn" disabled={loading}>
        {loading
          ? <><span className="loading-spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> {mode === "login" ? "Logging in…" : "Registering…"}</>
          : mode === "login" ? "Log In" : "Create Account"
        }
      </button>

      <p className="authSwitch">
        {mode === "login" ? (
          <>No account? <span onClick={() => { setMode("register"); }}>Register</span></>
        ) : (
          <>Already have an account? <span onClick={() => { setMode("login"); }}>Log In</span></>
        )}
      </p>
    </form>
  );
}
