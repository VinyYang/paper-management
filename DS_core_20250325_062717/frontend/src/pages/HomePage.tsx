import React, { useState } from 'react';
import { Typography, Row, Col, Card, Button, Space, Modal } from 'antd';
import { useNavigate } from 'react-router-dom';
import { 
  BookOutlined, 
  FileSearchOutlined, 
  RocketOutlined, 
  LoginOutlined, 
  UserAddOutlined,
  UserSwitchOutlined
} from '@ant-design/icons';
import AuthBackground from '../components/AuthBackground';
import Login from './Login';
import Register from './Register';
import { userApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const { Title, Paragraph } = Typography;

const HomePage: React.FC = () => {
  const [loginVisible, setLoginVisible] = useState(false);
  const [registerVisible, setRegisterVisible] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);
  const navigate = useNavigate();
  const { setToken, setUser } = useAuth();

  // 处理登录/注册按钮点击
  const handleAuthAction = (action: 'login' | 'register') => {
    if (action === 'login') {
      setLoginVisible(true);
      setRegisterVisible(false);
    } else {
      setLoginVisible(false);
      setRegisterVisible(true);
    }
  };

  // 游客模式登录
  const handleGuestLogin = async () => {
    try {
      setGuestLoading(true);
      // 调用游客登录API
      const response = await userApi.guestLogin();
      const { access_token } = response.data;
      
      // 存储token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // 获取用户信息
      const userResponse = await userApi.getCurrentUser();
      setUser(userResponse.data);
      
      // 跳转到文献搜索页面
      navigate('/scihub-search');
    } catch (error) {
      console.error('游客登录失败:', error);
    } finally {
      setGuestLoading(false);
    }
  };

  const features = [
    {
      icon: <BookOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
      title: '文献管理',
      description: '高效管理您的研究文献，支持多种分类和标签。创建个性化文献库，添加笔记和标签，轻松组织您的研究资料。'
    },
    {
      icon: <FileSearchOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
      title: '智能检索',
      description: '强大的检索功能，帮助您快速找到所需信息。支持全文搜索、DOI查询、高级筛选，让文献检索更加高效便捷。'
    },
    {
      icon: <RocketOutlined style={{ fontSize: 48, color: '#faad14' }} />,
      title: '知识图谱',
      description: '直观可视化您的研究领域，发现新连接。通过知识图谱技术，展示文献间的关联性，帮助您发现研究热点和新方向。'
    }
  ];

  return (
    <AuthBackground withOverlay={true}>
      <div>
        {/* 顶部导航 */}
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          right: 0, 
          padding: '20px', 
          zIndex: 100,
          display: 'flex',
          gap: '10px'
        }}>
          <Button 
            type="primary" 
            icon={<LoginOutlined />} 
            onClick={() => handleAuthAction('login')}
            style={{ background: '#1890ff', borderColor: '#1890ff' }}
          >
            登录
          </Button>
          <Button 
            icon={<UserAddOutlined />} 
            onClick={() => handleAuthAction('register')}
            style={{ background: 'rgba(255,255,255,0.9)', color: '#333' }}
          >
            注册
          </Button>
          <Button 
            icon={<UserSwitchOutlined />} 
            onClick={handleGuestLogin}
            loading={guestLoading}
            style={{ background: 'rgba(255,255,255,0.7)', color: '#555' }}
          >
            游客模式
          </Button>
        </div>

        {/* 主页内容区域 */}
        <div style={{ 
          minHeight: '100vh', 
          padding: '100px 20px 50px 20px'
        }}>
          <div 
            style={{ 
              textAlign: 'center', 
              maxWidth: '1000px', 
              margin: '0 auto 60px auto',
              padding: '30px',
            }}
          >
            <Title style={{ 
              color: 'white', 
              fontSize: '3.5rem', 
              marginBottom: '20px',
              textShadow: '0 2px 8px rgba(0,0,0,0.6)'
            }}>
              文献管理与知识发现系统
            </Title>
            <Paragraph style={{ 
              color: 'white', 
              fontSize: '1.4rem', 
              textAlign: 'center',
              marginBottom: '40px',
              textShadow: '0 1px 4px rgba(0,0,0,0.6)'
            }}>
              全方位的科研助手，帮助您高效管理文献、构建知识网络、促进科研创新
            </Paragraph>
            
            <Space size="large">
              <Button 
                type="primary" 
                size="large" 
                onClick={() => handleAuthAction('login')}
                style={{ height: '50px', fontSize: '1.1rem', padding: '0 30px', background: '#1890ff' }}
              >
                立即开始
              </Button>
              <Button 
                size="large" 
                onClick={() => navigate('/about')}
                style={{ height: '50px', fontSize: '1.1rem', padding: '0 30px', background: 'rgba(255,255,255,0.95)', color: '#333', border: '1px solid #d9d9d9' }}
              >
                了解更多
              </Button>
              <Button 
                size="large" 
                onClick={handleGuestLogin}
                loading={guestLoading}
                style={{ height: '50px', fontSize: '1.1rem', padding: '0 30px', background: 'rgba(255,255,255,0.8)', color: '#555', border: '1px solid #d9d9d9' }}
              >
                游客模式体验
              </Button>
            </Space>
          </div>

          {/* 功能介绍区域 */}
          <Row gutter={[40, 40]} style={{ maxWidth: '1200px', margin: '0 auto' }}>
            {features.map((feature, index) => (
              <Col xs={24} md={8} key={index}>
                <Card 
                  hoverable
                  className="feature-card"
                  style={{ 
                    height: '100%', 
                    textAlign: 'center', 
                    borderRadius: '12px',
                    overflow: 'hidden',
                    border: 'none',
                    background: 'rgba(255, 255, 255, 0.9)',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{ padding: '30px 20px' }}>
                    <div style={{ marginBottom: '20px' }}>{feature.icon}</div>
                    <Title level={3} style={{ color: '#333' }}>{feature.title}</Title>
                    <Paragraph style={{ fontSize: '16px', color: '#555' }}>{feature.description}</Paragraph>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>

          {/* 添加卡片悬停效果的CSS */}
          <style>{`
            .feature-card:hover {
              transform: translateY(-10px) scale(1.03);
              box-shadow: 0 15px 30px rgba(0,0,0,0.3);
              background: rgba(255, 255, 255, 0.98) !important;
            }
          `}</style>
        </div>

        {/* 登录模态框 */}
        <Modal
          open={loginVisible}
          footer={null}
          onCancel={() => setLoginVisible(false)}
          width={450}
          centered
          destroyOnClose
          className="auth-modal"
          maskStyle={{ backdropFilter: 'blur(5px)' }}
        >
          <Login />
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <span>还没有账号？</span>
            <Button 
              type="link" 
              onClick={() => {
                setLoginVisible(false);
                setRegisterVisible(true);
              }}
              style={{ color: '#1890ff', fontWeight: 'bold', padding: '0 5px' }}
            >
              立即注册
            </Button>
          </div>
        </Modal>

        {/* 注册模态框 */}
        <Modal
          open={registerVisible}
          footer={null}
          onCancel={() => setRegisterVisible(false)}
          width={500}
          centered
          destroyOnClose
          className="auth-modal"
          maskStyle={{ backdropFilter: 'blur(5px)' }}
        >
          <Register />
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <span>已有账号？</span>
            <Button 
              type="link" 
              onClick={() => {
                setRegisterVisible(false);
                setLoginVisible(true);
              }}
              style={{ color: '#1890ff', fontWeight: 'bold', padding: '0 5px' }}
            >
              立即登录
            </Button>
          </div>
        </Modal>

        {/* 添加模态框样式 */}
        <style>{`
          .auth-modal .ant-modal-content {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
          }
          .auth-modal .ant-modal-body {
            padding: 24px;
          }
        `}</style>
      </div>
    </AuthBackground>
  );
};

export default HomePage; 