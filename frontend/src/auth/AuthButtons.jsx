import { useAuth } from "..AuthContext";

export default function AuthButtons({ onLoginClick }) {
  const { token, logout } = useAuth();

  if (token) {
    return (
      <button className="btn logout" onClick={logout}>
        Logout
      </button>
    );
  }

  return (
    <button className="btn login" onClick={onLoginClick}>
      Login
    </button>
  );
}
