import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { message } from 'antd';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, token, user } = useAuth();
  
  useEffect(() => {
    if (!isAuthenticated) {
      console.log('用户未认证，准备重定向到登录页面', { 
        token, 
        isAuthenticated,
        hasLocalStorageToken: !!localStorage.getItem('token') 
      });
      message.info('请先登录');
    } else {
      console.log('用户已认证，允许访问受保护的路由', { token, user });
    }
  }, [isAuthenticated, token, user]);
  
  if (!isAuthenticated) {
    console.log('重定向到登录页面');
    return <Navigate to="/login" />;
  }
  
  return <>{children}</>;
};

export default ProtectedRoute; 