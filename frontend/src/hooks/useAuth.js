import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import client from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('adaptlab_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('adaptlab_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isAuthenticated = !!token && !!user;

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.post('/auth/login', { username, password });
      const { access_token, user: userData } = res.data;
      localStorage.setItem('adaptlab_token', access_token);
      localStorage.setItem('adaptlab_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.post('/auth/register', { username, email, password });
      const { access_token, user: userData } = res.data;
      localStorage.setItem('adaptlab_token', access_token);
      localStorage.setItem('adaptlab_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('adaptlab_token');
    localStorage.removeItem('adaptlab_user');
    setToken(null);
    setUser(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated, loading, error, login, register, logout, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default useAuth;
