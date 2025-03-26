import { api } from './core';
import { UserData } from './types';

// 用户相关API
export const userApi = {
  login: (data: { username: string; password: string }) => 
    api.post('/api/token', new URLSearchParams({
      'username': data.username,
      'password': data.password
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }),
     
  guestLogin: () => api.post('/api/users/guest'),
   
  register: (data: UserData) => api.post('/api/users/register', data),
   
  getCurrentUser: () => api.get('/api/users/me'),
   
  getUserPapers: () => api.get('/api/users/me/papers'),
   
  updateProfile: (data: UserData) => api.put('/api/users/me', data),
   
  uploadAvatar: (formData: FormData) => api.post('/api/users/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
   
  getAllUsers: () => api.get('/api/users'),
   
  deleteUser: (userId: number) => api.delete(`/api/users/${userId}`),
   
  activateCDK: (cdk: string) => api.post('/api/users/activate-cdk', { cdk })
}; 