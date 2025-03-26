import React, { useState, useEffect } from 'react';
import { Layout, Menu, Dropdown, Button, Avatar, Space } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  LogoutOutlined,
  FileSearchOutlined,
  ProjectOutlined,
  BookOutlined,
  StarOutlined,
  NodeIndexOutlined,
  SearchOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

const { Header: AntHeader } = Layout;

const HeaderComponent: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { themeMode, language } = useSettings();
  const [selectedKey, setSelectedKey] = useState<string>('');
  const isDarkMode = themeMode === 'dark' || (themeMode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  useEffect(() => {
    const pathname = location.pathname;
    if (pathname.startsWith('/library')) {
      setSelectedKey('library');
    } else if (pathname.startsWith('/notes')) {
      setSelectedKey('notes');
    } else if (pathname.startsWith('/knowledge-graph')) {
      setSelectedKey('knowledge-graph');
    } else if (pathname.startsWith('/paper-similarity')) {
      setSelectedKey('paper-similarity');
    } else if (pathname.startsWith('/recommendations')) {
      setSelectedKey('recommendations');
    } else if (pathname.startsWith('/scihub-search')) {
      setSelectedKey('scihub-search');
    }
  }, [location]);

  // 获取翻译文本
  const getTranslation = (zhText: string, enText: string) => {
    return language === 'zh_CN' ? zhText : enText;
  };

  const menuItems = [
    { key: '/library', label: getTranslation('文献库', 'Library'), icon: <BookOutlined /> },
    { key: '/knowledge-graph', label: getTranslation('知识图谱', 'Knowledge Graph'), icon: <NodeIndexOutlined /> },
    { key: '/paper-similarity', label: getTranslation('论文相似度分析', 'Paper Similarity'), icon: <BarChartOutlined /> },
    { key: '/recommendations', label: getTranslation('推荐', 'Recommendations'), icon: <StarOutlined /> },
    { key: '/scihub-search', label: getTranslation('文献搜索', 'Literature Search'), icon: <SearchOutlined /> },
    { key: '/projects', label: getTranslation('研究项目', 'Projects'), icon: <ProjectOutlined /> }
  ];

  const userMenu = (
    <Menu theme={isDarkMode ? 'dark' : 'light'}>
      <Menu.Item key="profile">
        <Link to="/profile">{getTranslation('个人资料', 'Profile')}</Link>
      </Menu.Item>
      <Menu.Item key="settings">
        <Link to="/settings">{getTranslation('设置', 'Settings')}</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" onClick={logout}>{getTranslation('退出登录', 'Logout')}</Menu.Item>
    </Menu>
  );

  // 根据当前主题设置标题和背景颜色
  const headerBackground = isDarkMode ? '#001529' : '#fff';
  const textColor = isDarkMode ? '#fff' : 'rgba(0, 0, 0, 0.85)';

  return (
    <AntHeader style={{ 
      position: 'fixed', 
      zIndex: 999, 
      width: '100%', 
      display: 'flex', 
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      background: headerBackground,
      boxShadow: isDarkMode ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.06)',
      color: textColor
    }}>
      <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
        <Link to="/" style={{ 
          fontSize: '18px', 
          fontWeight: 'bold', 
          marginRight: '24px',
          color: textColor 
        }}>
          {getTranslation('学术文献管理系统', 'Academic Literature Management System')}
        </Link>
        <Menu
          theme={isDarkMode ? 'dark' : 'light'}
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: <Link to={item.key}>{item.label}</Link>
          }))}
          style={{ border: 'none', flex: 1, background: headerBackground }}
        />
      </div>
      
      <Dropdown overlay={userMenu} trigger={['click']}>
        <Button type="text" style={{ marginLeft: '16px', color: textColor }}>
          <Space>
            <Avatar size="small" icon={<UserOutlined />} src={user?.avatar} />
            {user?.username || getTranslation('用户', 'User')}
          </Space>
        </Button>
      </Dropdown>
    </AntHeader>
  );
};

export default HeaderComponent as React.ComponentType; 