import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // Check if there's a stored token
        const token = localStorage.getItem('authToken');
        if (token) {
          // In a real app, you'd validate the token with the backend
          // For now, we'll simulate a logged-in user
          const mockUser = {
            id: 1,
            username: 'trader123',
            email: 'trader@example.com',
            fullName: 'John Trader',
            avatar: null,
          };
          setUser(mockUser);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials) => {
    try {
      setLoading(true);
      
      // In a real app, this would be an API call to your backend
      // For now, we'll simulate a successful login
      if (credentials.username === 'demo' && credentials.password === 'demo123') {
        const mockUser = {
          id: 1,
          username: credentials.username,
          email: 'demo@example.com',
          fullName: 'Demo User',
          avatar: null,
        };
        
        // Store auth token (in real app, this would come from backend)
        localStorage.setItem('authToken', 'mock-jwt-token');
        
        setUser(mockUser);
        setIsAuthenticated(true);
        
        return { success: true, user: mockUser };
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      
      // In a real app, this would be an API call to your backend
      // For now, we'll simulate a successful registration
      const newUser = {
        id: Date.now(),
        username: userData.username,
        email: userData.email,
        fullName: userData.fullName,
        avatar: null,
      };
      
      // Store auth token (in real app, this would come from backend)
      localStorage.setItem('authToken', 'mock-jwt-token');
      
      setUser(newUser);
      setIsAuthenticated(true);
      
      return { success: true, user: newUser };
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Clear stored auth data
      localStorage.removeItem('authToken');
      
      // Reset state
      setUser(null);
      setIsAuthenticated(false);
      
      return { success: true };
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setLoading(true);
      
      // In a real app, this would be an API call to your backend
      const updatedUser = { ...user, ...profileData };
      setUser(updatedUser);
      
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setLoading(true);
      
      // In a real app, this would be an API call to your backend
      // For now, we'll simulate success
      return { success: true };
    } catch (error) {
      console.error('Password change failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
