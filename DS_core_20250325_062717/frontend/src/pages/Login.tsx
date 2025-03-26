import React, { useState } from 'react';
import { Form, Input, Button, message, Typography, Divider, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { userApi } from '../services/api';

const { Title } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);
  const navigate = useNavigate();
  const { setToken, setUser } = useAuth();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      // 调用登录接口
      const tokenResponse = await userApi.login(values);
      const { access_token } = tokenResponse.data;
      
      // 存储token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // 获取用户信息
      const userResponse = await userApi.getCurrentUser();
      setUser(userResponse.data);
      
      message.success('登录成功');
      navigate('/scihub-search');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '登录失败';
      message.error(`登录失败: ${errorMsg}`);
      console.error('登录错误:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = async () => {
    setGuestLoading(true);
    try {
      console.log('尝试游客登录...');
      const response = await userApi.guestLogin();
      console.log('游客登录API响应:', response);
      
      if (response.data && response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        setToken(response.data.access_token);
        message.success('游客登录成功');
        
        // 获取用户信息
        try {
          const userResponse = await userApi.getCurrentUser();
          console.log('获取游客用户信息成功:', userResponse.data);
          setUser(userResponse.data);
          navigate('/dashboard');
        } catch (userError) {
          console.error('获取游客用户信息失败:', userError);
        }
      } else {
        console.error('游客登录响应格式不正确:', response.data);
        message.error('游客登录失败，请稍后再试');
      }
    } catch (error: any) {
      console.error('游客登录出错:', error);
      console.error('错误详情:', error.response?.data || error.message);
      message.error(`游客登录失败: ${error.response?.data?.detail || error.message || '未知错误'}`);
    } finally {
      setGuestLoading(false);
    }
  };

  // 修改临时测试函数，使用正确的API路径
  const testGuestLogin = async () => {
    setGuestLoading(true);
    try {
      console.log('使用fetch直接测试游客登录...');
      
      // 使用正确的API路径
      const response = await fetch('http://localhost:8003/api/users/guest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // 添加空请求体
        body: JSON.stringify({})
      });
      
      console.log('游客登录状态码:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP错误 ${response.status}: ${await response.text()}`);
      }
      
      const data = await response.json();
      console.log('直接测试游客登录响应:', data);
      
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        message.success('游客登录成功');
        
        // 获取用户信息
        try {
          const userResponse = await userApi.getCurrentUser();
          console.log('获取游客用户信息成功:', userResponse.data);
          setUser(userResponse.data);
          navigate('/dashboard');
        } catch (userError) {
          console.error('获取游客用户信息失败:', userError);
        }
      } else {
        console.error('游客登录响应格式不正确:', data);
        message.error(`游客登录失败: ${data.detail || '请稍后再试'}`);
      }
    } catch (error: any) {
      console.error('游客登录出错:', error);
      message.error(`游客登录失败: ${error.message || '未知错误'}`);
    } finally {
      setGuestLoading(false);
    }
  };

  // 无边框输入框样式
  const borderlessInputStyle = {
    height: '45px',
    background: 'rgba(0, 0, 0, 0.02)',
    borderRadius: '4px',
    border: 'none',
    boxShadow: 'none'
  };

  return (
    <div className="login-form-container">
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30, color: '#333' }}>
        登录系统
      </Title>
      <Form
        name="login"
        onFinish={onFinish}
        size="large"
        style={{ maxWidth: '400px', margin: '0 auto' }}
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名' }]}
        >
          <Input 
            prefix={<UserOutlined style={{ color: 'rgba(0,0,0,.25)' }} />} 
            placeholder="用户名"
            style={borderlessInputStyle}
          />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码' }]}
        >
          <Input.Password 
            prefix={<LockOutlined style={{ color: 'rgba(0,0,0,.25)' }} />} 
            placeholder="密码" 
            style={borderlessInputStyle}
          />
        </Form.Item>
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading} 
            block
            style={{ height: '45px', fontSize: '16px' }}
          >
            登录
          </Button>
        </Form.Item>
        
        <Divider style={{ fontSize: '14px', color: '#999' }}>或</Divider>
        
        <Form.Item>
          <Button 
            type="default"
            onClick={testGuestLogin}
            loading={guestLoading}
            block
            style={{ height: '45px', fontSize: '16px' }}
          >
            使用游客模式
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Login; 