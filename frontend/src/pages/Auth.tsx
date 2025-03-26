import React, { useState, useEffect } from 'react';
import { Spin } from 'antd';
import { useAuth } from '../contexts/AuthContext';
import { Navigate, useLocation } from 'react-router-dom';

const Auth: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [redirectTo, setRedirectTo] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 检查是否有重定向目标路径
    const params = new URLSearchParams(location.search);
    const redirect = params.get('redirect');
    if (redirect) {
      setRedirectTo(redirect);
    }
    // 短暂延迟以确保认证状态已加载
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [location]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="验证身份中..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={`/login${redirectTo ? `?redirect=${redirectTo}` : ''}`} />;
  }

  return <Navigate to={redirectTo || '/'} />;
};

export default Auth as React.ComponentType; 