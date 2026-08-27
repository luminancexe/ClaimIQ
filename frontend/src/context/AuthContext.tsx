import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { UserProfile, UserRole, LoginRequest } from '../types';
import { login as apiLogin, getMe } from '../api/auth';
import {
  getStoredAccessToken,
  setStoredTokens,
  clearStoredTokens,
} from '../api/client';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    try {
      const profile = await getMe();
      setUser(profile);
      setError(null);
    } catch {
      setUser(null);
      clearStoredTokens();
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = getStoredAccessToken();
    if (token) {
      fetchProfile();
    } else {
      setIsLoading(false);
    }

    const handleAuthExpired = () => {
      setUser(null);
      clearStoredTokens();
    };

    window.addEventListener('claimiq:auth:expired', handleAuthExpired);
    return () => {
      window.removeEventListener('claimiq:auth:expired', handleAuthExpired);
    };
  }, [fetchProfile]);

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenData = await apiLogin(credentials);
      setStoredTokens(tokenData.access_token, tokenData.refresh_token);
      const profile = await getMe();
      setUser(profile);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Invalid credentials';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    clearStoredTokens();
    setUser(null);
    setError(null);
  };

  const hasRole = (...roles: UserRole[]): boolean => {
    if (!user) return false;
    if (user.role === 'ADMIN') return true; // Admin has universal role access
    return roles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export const ProtectedRoute: React.FC<{ children: ReactNode; allowedRoles?: UserRole[] }> = ({
  children,
  allowedRoles,
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-10 h-10 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin"></div>
          <p className="text-xs font-mono tracking-widest text-slate-400 uppercase">Authenticating ClaimIQ Session...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <NavigateToLogin from={location.pathname} />;
  }

  if (allowedRoles && user && user.role !== 'ADMIN' && !allowedRoles.includes(user.role)) {
    return (
      <div className="p-8 text-center bg-surface-card border border-rose-500/30 rounded-lg max-w-md mx-auto my-12">
        <h2 className="text-xl font-bold text-rose-400 mb-2">Access Restricted</h2>
        <p className="text-sm text-slate-400 mb-4">
          Your role (<span className="font-mono text-cyan-400">{user.role}</span>) does not have permission to view this module.
        </p>
        <button
          onClick={() => window.history.back()}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded border border-slate-700 transition"
        >
          Go Back
        </button>
      </div>
    );
  }

  return <>{children}</>;
};

const NavigateToLogin: React.FC<{ from: string }> = ({ from }) => {
  const navigate = useNavigate();
  useEffect(() => {
    navigate('/login', { replace: true, state: { from } });
  }, [navigate, from]);
  return null;
};
