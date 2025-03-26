import React from 'react';
import { Layout, Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  BookOutlined,
  FileTextOutlined,
  ShareAltOutlined,
  UserOutlined,
  LoginOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Header } = Layout;

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/papers',
      icon: <BookOutlined />,
      label: <Link to="/papers">文献</Link>,
    },
    {
      key: '/notes',
      icon: <FileTextOutlined />,
      label: <Link to="/notes">笔记</Link>,
    },
    {
      key: '/knowledge-graph',
      icon: <ShareAltOutlined />,
      label: <Link to="/knowledge-graph">知识图谱</Link>,
    },
    {
      key: '/recommendations',
      icon: <BookOutlined />,
      label: <Link to="/recommendations">推荐</Link>,
    },
  ];

  const userMenuItems = user ? [
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: <Link to="/profile">个人中心</Link>,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout,
    },
  ] : [
    {
      key: '/login',
      icon: <LoginOutlined />,
      label: <Link to="/login">登录</Link>,
    },
    {
      key: '/register',
      icon: <UserOutlined />,
      label: <Link to="/register">注册</Link>,
    },
  ];

  return (
    <Header style={{ background: '#fff', padding: 0 }}>
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={[...menuItems, ...userMenuItems]}
        style={{ lineHeight: '64px' }}
      />
    </Header>
  );
};

export default Navbar; 