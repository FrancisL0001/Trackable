// Authentication context: holds the current user, handles login/register/logout,
// and wires the API client's 401 handler to force logout.
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getToken, setToken, setUnauthorizedHandler } from "../api/client";
import { authApi } from "../api/endpoints";
import type { User, UserUpdate } from "../api/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  updateProfile: (input: UserUpdate) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  // On mount, restore the session from a stored token.
  useEffect(() => {
    setUnauthorizedHandler(logout);
    let active = true;
    (async () => {
      if (!getToken()) {
        setLoading(false);
        return;
      }
      try {
        const me = await authApi.me();
        if (active) setUser(me);
      } catch {
        if (active) logout();
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
      setUnauthorizedHandler(null);
    };
  }, [logout]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    setToken(res.access_token);
    setUser(res.user);
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      const res = await authApi.register({ email, password, full_name: fullName });
      setToken(res.access_token);
      setUser(res.user);
    },
    []
  );

  const updateProfile = useCallback(async (input: UserUpdate) => {
    const me = await authApi.updateMe(input);
    setUser(me);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, updateProfile, logout }),
    [user, loading, login, register, updateProfile, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
