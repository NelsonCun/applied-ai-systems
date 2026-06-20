import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import apiClient from "../api/client";


const AuthContext = createContext(null);

const TOKEN_KEY = "smartinvoice_token";
const USER_KEY = "smartinvoice_user";


function readStoredUser() {
  const rawUser = localStorage.getItem(
    USER_KEY,
  );

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}


export function AuthProvider({ children }) {
  const [user, setUser] = useState(
    readStoredUser,
  );

  const [loading, setLoading] =
    useState(true);

  const token = localStorage.getItem(
    TOKEN_KEY,
  );


  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);


  const loadCurrentUser =
    useCallback(async () => {
      const currentToken =
        localStorage.getItem(TOKEN_KEY);

      if (!currentToken) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.get(
          "/auth/me",
        );

        localStorage.setItem(
          USER_KEY,
          JSON.stringify(response.data),
        );

        setUser(response.data);
      } catch {
        clearSession();
      } finally {
        setLoading(false);
      }
    }, [clearSession]);


  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);


  const login = useCallback(
    async (identifier, password) => {
      const response = await apiClient.post(
        "/auth/login",
        {
          identifier,
          password,
        },
      );

      const {
        access_token: accessToken,
        user: authenticatedUser,
      } = response.data;

      localStorage.setItem(
        TOKEN_KEY,
        accessToken,
      );

      localStorage.setItem(
        USER_KEY,
        JSON.stringify(
          authenticatedUser,
        ),
      );

      setUser(authenticatedUser);

      return authenticatedUser;
    },
    [],
  );


  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);


  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(
        user && token,
      ),
      login,
      logout,
      refreshUser: loadCurrentUser,
    }),
    [
      user,
      loading,
      token,
      login,
      logout,
      loadCurrentUser,
    ],
  );


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth debe utilizarse dentro de AuthProvider",
    );
  }

  return context;
}
