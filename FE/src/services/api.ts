"use client";

import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include auth token in requests
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage (only in browser)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth service functions
export const authService = {
  login: async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  register: async (username: string, email: string, password: string) => {
    try {
      const response = await api.post('/auth/register', { username, email, password });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('authToken');
  },
  
  getCurrentUser: async () => {
    try {
      const response = await api.get('/users/me');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};


// wallets
export const walletService = {
  // Get active wallets
  getWallets: async () => {
    try {
      const response = await api.get('/wallets/');
      return response.data.wallets || [];
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Get deleted wallets
  getDeletedWallets: async () => {
    try {
      const response = await api.get('/wallets/deleted');
      return response.data.deleted_wallets || []; 
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Create new wallet
  createWallet: async (data: { name: string; balance: number; currency: string }) => {
    try {
      const response = await api.post('/wallets/create', data);
      return response.data.wallet;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Update wallet
  updateWallet: async (id: string, data: { name: string; currency: string }) => {
    try {
      const response = await api.put(`/wallets/update/${id}`, data);
      return response.data.wallet;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Soft delete wallet
  deleteWallet: async (id: string) => {
    try {
      await api.patch(`/wallets/soft_delete/${id}`);
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Restore wallet
  restoreWallet: async (id: string) => {
    try {
      await api.patch(`/wallets/restore/${id}`);
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};


// Categories
export const categoryService = {
  // Get active categories
  getCategories: async () => {
    try {
      const response = await api.get('/categories/');
      return response.data.categories || [];
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Get deleted categories
  getDeletedCategories: async () => {
    try {
      const response = await api.get('/categories/deleted');
      return response.data.deleted_categories|| []; 
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Create new category
  createCategory: async (data: { name: string }) => {
    try {
      const response = await api.post('/categories/create', data);
      return response.data.category;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Update category
  updateCategory: async (id: string, data: { name: string }) => {
    try {
      const response = await api.put(`/categories/update/${id}`, data);
      return response.data.category;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Soft delete category
  deleteCategory: async (id: string) => {
    try {
      await api.patch(`/categories/soft_delete/${id}`);
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Restore category
  restoreCategory: async (id: string) => {
    try {
      await api.patch(`/categories/restore/${id}`);
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};


export default api;
