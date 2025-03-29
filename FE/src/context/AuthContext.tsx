"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '@/services/api';

interface User {
  id: string;
  name: string;
  email: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState<boolean>(false);

  // This effect only runs once on initial load to check for existing auth
  useEffect(() => {
    const checkUserLoggedIn = async () => {
      try {
        console.log('AuthContext - Initializing auth check');
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('authToken');
          console.log('AuthContext - Token exists on init:', !!token);
          
          // Only try to get user data if a token exists
          if (token) {
            try {
              const userData = await authService.getCurrentUser();
              console.log('AuthContext - User data received on init:', userData);
              setUser(userData);
            } catch (apiErr) {
              console.error('AuthContext - API Error on init:', apiErr);
              // Clear token if API call fails
              localStorage.removeItem('authToken');
            }
          }
        }
      } catch (err) {
        console.error('AuthContext - Failed to initialize auth:', err);
      } finally {
        // Always mark as initialized and not loading, regardless of result
        setInitialized(true);
        setLoading(false);
      }
    };

    checkUserLoggedIn();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      console.log('AuthContext - Attempting login');
      const data = await authService.login(email, password);
      console.log('AuthContext - Login successful, user data:', data.user);
      
      // Set user in state
      setUser(data.user);
      
      // Return data for additional handling if needed
      return data;
    } catch (err: any) {
      console.error('AuthContext - Login failed:', err);
      setError(err.response?.data?.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };
  const register = async (name: string, email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      await authService.register(name, email, password);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    console.log('AuthContext - Logging out');
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};