import React, { createContext, useState, useEffect, useContext } from 'react';
import { userApi } from '../services/api';

// 创建认证上下文
export const AuthContext = createContext<{
  user: any | null;
  token: string | null;
  setUser: React.Dispatch<React.SetStateAction<any | null>>;
  setToken: React.Dispatch<React.SetStateAction<string | null>>;
  isAuthenticated: boolean;
  logout: () => void;
  refreshUser: () => Promise<void>;
}>({
  user: null,
  token: null,
  setUser: () => {},
  setToken: () => {},
  isAuthenticated: false,
  logout: () => {},
  refreshUser: async () => {},
});

// 认证提供者组件
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!token;

  // 添加调试信息
  useEffect(() => {
    console.log('认证状态更新:', { token, isAuthenticated });
  }, [token, isAuthenticated]);

  const logout = () => {
    console.log('用户登出');
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    // 重定向到首页而不是登录页
    window.location.href = '/';
  };

  const refreshUser = async () => {
    if (token) {
      try {
        console.log('刷新用户信息...');
        const response = await userApi.getCurrentUser();
        console.log('刷新用户信息成功:', response.data);
        setUser(response.data);
      } catch (error) {
        console.error('刷新用户信息失败', error);
      }
    }
  };

  useEffect(() => {
    const fetchCurrentUser = async () => {
      if (token) {
        try {
          console.log('正在获取当前用户信息...');
          const response = await userApi.getCurrentUser();
          console.log('获取用户信息成功:', response.data);
          setUser(response.data);
        } catch (error) {
          console.error('获取当前用户失败', error);
          logout();
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    fetchCurrentUser();
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, token, setUser, setToken, isAuthenticated, logout, refreshUser }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// 使用认证上下文的自定义钩子
export const useAuth = () => useContext(AuthContext); 