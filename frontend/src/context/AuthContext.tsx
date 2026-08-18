'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';
import { useRouter, usePathname } from 'next/navigation';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: Record<string, string>) => Promise<void>;
  register: (data: Record<string, string>) => Promise<void>;
  logout: () => Promise<void>;
  setAuthStatus: (status: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();
  const pathname = usePathname();

  const setAuthStatus = (status: boolean) => {
    setIsAuthenticated(status);
    setIsLoading(false);
  };

  useEffect(() => {
    // Auth check is now deferred to ProfileProvider to avoid duplicate /profile requests.
    // AuthProvider simply initializes the auth state via setAuthStatus called by ProfileProvider.
  }, []);

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated && pathname !== '/login' && pathname !== '/register') {
        router.push('/login');
      } else if (isAuthenticated && (pathname === '/login' || pathname === '/register')) {
        router.push('/');
      }
    }
  }, [isLoading, isAuthenticated, pathname, router]);

  const login = async (data: Record<string, string>) => {
    await api.login(data);
    setIsAuthenticated(true);
    router.push('/');
  };

  const register = async (data: Record<string, string>) => {
    await api.register(data);
    setIsAuthenticated(true);
    router.push('/');
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.error('Logout failed', e);
    } finally {
      setIsAuthenticated(false);
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, register, logout, setAuthStatus }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
