import { useState } from "react";
import { apiFetch } from "../api/api";

export default function RegisterForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function submit(e) {
    e.preventDefault();
    await apiFetch("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    alert("Registered. You can login now.");
  }

  return (
    <form onSubmit={submit} className="card">
      <h3>Register</h3>
      <input value={email} onChange={e => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button>Register</button>
    </form>
  );
}
