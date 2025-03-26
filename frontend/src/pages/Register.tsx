import React, { useState } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { UserOutlined, MailOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons';
import { userApi } from '../services/api';

const { Title } = Typography;

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    // 检查密码确认
    if (values.password !== values.confirm) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      // 调用后端注册接口
      await userApi.register({
        username: values.username,
        email: values.email,
        password: values.password
      });
      
      message.success('注册成功');
      navigate('/');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '注册失败，请稍后再试';
      message.error(errorMsg);
      console.error('注册错误:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-form-container">
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30, color: '#333' }}>
        创建账号
      </Title>
      <Form
        name="register"
        onFinish={onFinish}
        layout="vertical"
        style={{ maxWidth: '400px', margin: '0 auto' }}
        className="register-form"
      >
        <Form.Item
          name="username"
          label={<span style={{ color: '#333', fontWeight: 500 }}>用户名</span>}
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '用户名至少3个字符' }
          ]}
        >
          <Input 
            prefix={<UserOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
            placeholder="请输入用户名" 
            style={{ height: '45px' }}
          />
        </Form.Item>

        <Form.Item
          name="email"
          label={<span style={{ color: '#333', fontWeight: 500 }}>邮箱</span>}
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]}
        >
          <Input 
            prefix={<MailOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
            placeholder="请输入邮箱" 
            style={{ height: '45px' }}
          />
        </Form.Item>

        <Form.Item
          name="password"
          label={<span style={{ color: '#333', fontWeight: 500 }}>密码</span>}
          rules={[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少6个字符' }
          ]}
        >
          <Input.Password 
            prefix={<LockOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
            placeholder="请输入密码" 
            style={{ height: '45px' }}
          />
        </Form.Item>

        <Form.Item
          name="confirm"
          label={<span style={{ color: '#333', fontWeight: 500 }}>确认密码</span>}
          rules={[
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致'));
              },
            }),
          ]}
        >
          <Input.Password 
            prefix={<SafetyOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
            placeholder="请确认密码" 
            style={{ height: '45px' }}
          />
        </Form.Item>

        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            size="large" 
            block 
            loading={loading}
            style={{ height: '45px', fontSize: '16px' }}
          >
            注册
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Register; 