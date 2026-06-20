import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


export default function ProtectedRoute({
  children,
}) {
  const {
    loading,
    isAuthenticated,
  } = useAuth();

  if (loading) {
    return (
      <div className="screen-loader">
        <div className="loader-ring" />

        <p>Validando sesión...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return children;
}
