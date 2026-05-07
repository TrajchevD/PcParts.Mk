import { createContext, useCallback, useContext, useState } from "react";

const AuthContext = createContext(null);

/**
 * Decode a JWT payload without verifying the signature.
 * Used only for reading `exp` to pre-screen expired tokens client-side.
 */
function decodePayload(token) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

function isTokenExpired(token) {
  const payload = decodePayload(token);
  if (!payload?.exp) return false;
  // Give a 30-second grace period
  return payload.exp < Math.floor(Date.now() / 1000) + 30;
}

function getStoredToken() {
  const raw = localStorage.getItem("token");
  if (!raw) return null;
  if (isTokenExpired(raw)) {
    localStorage.removeItem("token");
    return null;
  }
  return raw;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken);

  const login = useCallback((jwt) => {
    localStorage.setItem("token", jwt);
    setToken(jwt);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
