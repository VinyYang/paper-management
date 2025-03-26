import { api } from './core';
import { UserData } from './types';

// 用户认证相关API
export const authApi = {
  login: (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  register: (user: UserData) => 
    api.post('/api/auth/register', user),
  
  getCurrentUser: () => 
    api.get('/api/users/me'),
  
  updateProfile: (userData: UserData) => 
    api.put('/api/users/me', userData),
  
  changePassword: (oldPassword: string, newPassword: string) => 
    api.post('/api/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  
  resetPassword: (email: string) => 
    api.post('/api/auth/reset-password', { email }),
  
  confirmResetPassword: (token: string, password: string) => 
    api.post('/api/auth/confirm-reset-password', { token, password }),
  
  verifyEmail: (token: string) => 
    api.get(`/api/auth/verify-email/${token}`),
  
  resendVerification: (email: string) => 
    api.post('/api/auth/resend-verification', { email })
}; 