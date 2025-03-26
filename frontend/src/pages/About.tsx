import React from 'react';
import { Typography, Row, Col, Card, Space, Button, Divider } from 'antd';
import { 
  BookOutlined, 
  CheckCircleOutlined,
  TeamOutlined,
  AimOutlined,
  ThunderboltOutlined,
  EnvironmentOutlined,
  ArrowLeftOutlined,
  MailOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import AuthBackground from '../components/AuthBackground';

const { Title, Paragraph, Text } = Typography;

const About: React.FC = () => {
  const navigate = useNavigate();

  const systemFeatures = [
    {
      icon: <BookOutlined style={{ fontSize: 36, color: '#1890ff' }} />,
      title: '文献管理与组织',
      description: '支持PDF文献上传、元数据提取、分类标签管理，实现文献的智能化管理与组织。'
    },
    {
      icon: <ThunderboltOutlined style={{ fontSize: 36, color: '#52c41a' }} />,
      title: '智能检索与推荐',
      description: '基于机器学习的文献检索与推荐系统，帮助研究者发现相关文献和研究方向。'
    },
    {
      icon: <TeamOutlined style={{ fontSize: 36, color: '#faad14' }} />,
      title: '学术协作功能',
      description: '提供团队共享库、协作笔记、研究讨论等功能，促进科研团队协作。'
    }
  ];

  return (
    <AuthBackground withOverlay={true}>
      <div style={{ minHeight: '100vh', padding: '40px 20px' }}>
        {/* 返回按钮 */}
        <Button 
          type="primary"
          icon={<ArrowLeftOutlined />} 
          style={{ 
            marginBottom: 30,
            background: 'rgba(24, 144, 255, 0.85)',
            borderColor: 'transparent',
            boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)'
          }}
          onClick={() => navigate('/')}
        >
          返回首页
        </Button>

        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          {/* 关于我们部分 */}
          <Card 
            style={{ 
              marginBottom: '40px',
              borderRadius: '16px',
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)'
            }}
            bordered={false}
          >
            <Title level={2} style={{ textAlign: 'center', color: '#1a3f62', marginBottom: 40, fontWeight: 600 }}>
              关于我们
            </Title>
            
            <Row gutter={[30, 30]}>
              <Col xs={24} md={12}>
                <div style={{ marginBottom: 30 }}>
                  <Title level={3} style={{ display: 'flex', alignItems: 'center', color: '#1a3f62' }}>
                    <AimOutlined style={{ marginRight: 10, color: '#1890ff' }} /> 我们的使命
                  </Title>
                  <Paragraph style={{ fontSize: '16px', lineHeight: '1.8', color: '#333' }}>
                    为科研工作者打造一站式文献管理与知识发现平台，通过智能技术降低科研门槛，
                    提高研究效率，促进学术创新与交流。我们致力于将人工智能与知识管理相结合，
                    为学术研究提供强大的数字化助力。
                  </Paragraph>
                </div>
                
                <div>
                  <Title level={3} style={{ display: 'flex', alignItems: 'center', color: '#1a3f62' }}>
                    <EnvironmentOutlined style={{ marginRight: 10, color: '#1890ff' }} /> 我们的愿景
                  </Title>
                  <Paragraph style={{ fontSize: '16px', lineHeight: '1.8', color: '#333' }}>
                    成为全球领先的学术资源管理与知识发现平台，推动开放科学发展，
                    构建更加开放、高效、创新的学术生态系统。我们期望通过先进技术，
                    打破信息孤岛，促进跨学科知识融合与创新。
                  </Paragraph>
                </div>
              </Col>
              
              <Col xs={24} md={12}>
                <Title level={3} style={{ display: 'flex', alignItems: 'center', marginBottom: 20, color: '#1a3f62' }}>
                  <CheckCircleOutlined style={{ marginRight: 10, color: '#52c41a' }} /> 核心优势
                </Title>
                <ul style={{ fontSize: '16px', paddingLeft: 20 }}>
                  <li style={{ marginBottom: 15, color: '#333' }}>
                    <Text strong style={{ color: '#1a3f62' }}>智能文献管理</Text> - 自动提取元数据，智能分类与标签管理
                  </li>
                  <li style={{ marginBottom: 15, color: '#333' }}>
                    <Text strong style={{ color: '#1a3f62' }}>知识网络构建</Text> - 可视化文献关系，发现研究热点与趋势
                  </li>
                  <li style={{ marginBottom: 15, color: '#333' }}>
                    <Text strong style={{ color: '#1a3f62' }}>智能检索推荐</Text> - 个性化文献推荐，相关研究方向发现
                  </li>
                  <li style={{ marginBottom: 15, color: '#333' }}>
                    <Text strong style={{ color: '#1a3f62' }}>多样化数据源</Text> - 整合多个学术数据库，提供一站式检索
                  </li>
                  <li style={{ marginBottom: 15, color: '#333' }}>
                    <Text strong style={{ color: '#1a3f62' }}>开放API接口</Text> - 支持与其他研究工具无缝集成
                  </li>
                  <li style={{ marginBottom: 15, color: '#333' }}>
                    <Text strong style={{ color: '#1a3f62' }}>团队协作功能</Text> - 支持团队共享与协作，促进学术交流
                  </li>
                </ul>
              </Col>
            </Row>
          </Card>
          
          {/* 系统功能部分 */}
          <Card 
            style={{ 
              marginBottom: '40px',
              borderRadius: '16px',
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)'
            }}
            bordered={false}
          >
            <Title level={2} style={{ textAlign: 'center', color: '#1a3f62', marginBottom: 40, fontWeight: 600 }}>
              系统功能
            </Title>
            
            <Row gutter={[30, 30]}>
              {systemFeatures.map((feature, index) => (
                <Col xs={24} md={8} key={index}>
                  <Card 
                    hoverable 
                    style={{ 
                      height: '100%',
                      borderRadius: '12px',
                      background: 'rgba(255, 255, 255, 0.8)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                      transition: 'all 0.3s ease',
                      border: 'none'
                    }}
                    className="feature-card"
                  >
                    <div style={{ textAlign: 'center', marginBottom: 20 }}>
                      {feature.icon}
                    </div>
                    <Title level={4} style={{ textAlign: 'center', marginBottom: 16, color: '#1a3f62' }}>
                      {feature.title}
                    </Title>
                    <Paragraph style={{ fontSize: '15px', textAlign: 'center', color: '#333' }}>
                      {feature.description}
                    </Paragraph>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>

          {/* 联系我们部分 */}
          <Card 
            style={{ 
              marginBottom: '40px',
              borderRadius: '16px',
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
              textAlign: 'center'
            }}
            bordered={false}
          >
            <Title level={2} style={{ color: '#1a3f62', marginBottom: 30, fontWeight: 600 }}>
              联系我们
            </Title>
            
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Paragraph style={{ fontSize: '16px', color: '#333' }}>
                如果您对我们的系统有任何疑问、建议或合作意向，欢迎通过以下方式联系我们：
              </Paragraph>
              
              <Button 
                type="primary" 
                icon={<MailOutlined />} 
                size="large"
                onClick={() => window.open('http://cis.swu.edu.cn/', '_blank')}
                style={{
                  height: '46px',
                  borderRadius: '8px',
                  background: 'rgba(24, 144, 255, 0.85)',
                  borderColor: 'transparent',
                  boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)'
                }}
              >
                联系我们
              </Button>
              
              <Paragraph style={{ marginTop: 20, fontSize: '15px', color: '#333' }}>
                邮箱：swujxy@swu.edu.cn<br />
                地址：中国 重庆市 北碚区 西南大学
              </Paragraph>
            </Space>
          </Card>
          
          {/* 返回首页按钮 */}
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <Button 
              type="primary" 
              size="large" 
              onClick={() => navigate('/')}
              style={{ 
                height: '46px', 
                padding: '0 30px',
                borderRadius: '8px',
                background: 'rgba(24, 144, 255, 0.85)',
                borderColor: 'transparent',
                boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)'
              }}
            >
              返回首页
            </Button>
          </div>
        </div>

        {/* 添加悬停效果的 CSS */}
        <style>{`
          .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.12) !important;
          }
        `}</style>
      </div>
    </AuthBackground>
  );
};

export default About; 