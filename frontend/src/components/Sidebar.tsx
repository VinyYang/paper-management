import React from 'react';
import { Layout, Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import {
  FileTextOutlined,
  BookOutlined,
  ShareAltOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <FileTextOutlined />,
      label: <Link to="/">文献管理</Link>,
    },
    {
      key: '/knowledge-graph',
      icon: <ShareAltOutlined />,
      label: <Link to="/knowledge-graph">知识图谱</Link>,
    },
    {
      key: '/notes',
      icon: <BookOutlined />,
      label: <Link to="/notes">笔记系统</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">系统设置</Link>,
    },
  ];

  return (
    <Sider width={200} style={{ background: '#fff' }}>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        style={{ height: '100%', borderRight: 0 }}
        items={menuItems}
      />
    </Sider>
  );
};

export default Sidebar; 