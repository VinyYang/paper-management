import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Typography, message, Spin, Avatar, Row, Col, Progress, Space } from 'antd';
import { UserOutlined, CloudUploadOutlined, KeyOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { userApi, paperApi } from '../services/api';

const { Title, Paragraph, Text } = Typography;

const Profile: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [form] = Form.useForm();
  const [cdkForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [cdkLoading, setCdkLoading] = useState(false);
  const [storageInfo, setStorageInfo] = useState<{
    storage_capacity?: number;
    storage_used?: number;
    storage_free?: number;
    usage_percentage?: number;
    total_space_mb?: number;
    used_space_mb?: number;
  }>({
    storage_capacity: 1024,
    storage_used: 0,
    storage_free: 1024,
    usage_percentage: 0,
  });

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
      });
      // 获取存储信息
      fetchStorageInfo();
    }
  }, [user, form]);

  // 获取存储空间信息
  const fetchStorageInfo = async () => {
    try {
      const response = await paperApi.getStorageInfo();
      // 处理字段名不一致的情况
      const data = response.data;
      const standardizedData = {
        storage_capacity: data.storage_capacity || data.total_space_mb || 1024,
        storage_used: data.storage_used || data.used_space_mb || 0,
        storage_free: data.storage_free || (data.total_space_mb ? data.total_space_mb - data.used_space_mb : 1024),
        usage_percentage: data.usage_percentage || (data.total_space_mb ? (data.used_space_mb / data.total_space_mb * 100) : 0),
        used_space_mb: data.used_space_mb,
        total_space_mb: data.total_space_mb
      };
      setStorageInfo(standardizedData);
      console.log('获取存储信息成功:', standardizedData);
    } catch (error) {
      console.error('获取存储信息失败', error);
    }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      await userApi.updateProfile(values);
      message.success('个人资料更新成功');
      // 刷新用户信息
      refreshUser && refreshUser();
    } catch (error) {
      console.error('更新个人资料失败', error);
      message.error('更新个人资料失败');
    } finally {
      setLoading(false);
    }
  };

  // 激活CDK
  const handleActivateCDK = async (values: { cdk: string }) => {
    setCdkLoading(true);
    try {
      await userApi.activateCDK(values.cdk);
      message.success('CDK激活成功，存储空间已增加');
      // 重新获取存储信息
      fetchStorageInfo();
      // 清空表单
      cdkForm.resetFields();
    } catch (error) {
      console.error('激活CDK失败', error);
      message.error('激活CDK失败，请检查CDK是否有效或已被使用');
    } finally {
      setCdkLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[24, 24]}>
        <Col xs={24} md={16}>
          <Card>
            <Title level={3}>个人资料</Title>
            <Paragraph>
              在这里查看和更新您的个人信息。
            </Paragraph>
            
            <Spin spinning={loading}>
              <Row gutter={24}>
                <Col xs={24} md={8} style={{ marginBottom: '24px', textAlign: 'center' }}>
                  <div style={{ marginBottom: '16px' }}>
                    <Avatar icon={<UserOutlined />} size={120} />
                  </div>
                  
                  <Paragraph type="secondary" style={{ marginTop: '8px' }}>
                    系统默认头像
                  </Paragraph>
                </Col>
                
                <Col xs={24} md={16}>
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                  >
                    <Form.Item
                      name="username"
                      label="用户名"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input disabled />
                    </Form.Item>
                    
                    <Form.Item
                      name="email"
                      label="电子邮箱"
                      rules={[
                        { required: true, message: '请输入电子邮箱' },
                        { type: 'email', message: '请输入有效的电子邮箱' }
                      ]}
                    >
                      <Input />
                    </Form.Item>
                    
                    <Form.Item
                      name="password"
                      label="新密码"
                      rules={[{ 
                        min: 6, 
                        message: '密码长度至少为6个字符' 
                      }]}
                      extra="如不需更改密码，请留空"
                    >
                      <Input.Password />
                    </Form.Item>
                    
                    <Form.Item
                      name="confirmPassword"
                      label="确认新密码"
                      dependencies={['password']}
                      rules={[
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
                      <Input.Password />
                    </Form.Item>
                    
                    <Form.Item>
                      <Button type="primary" htmlType="submit">
                        保存修改
                      </Button>
                    </Form.Item>
                  </Form>
                </Col>
              </Row>
            </Spin>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 存储空间信息卡片 */}
            <Card>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
                  <CloudUploadOutlined style={{ fontSize: '24px', marginRight: '12px', color: '#1890ff' }} />
                  <Title level={4} style={{ margin: 0 }}>存储空间</Title>
                </div>
                <Paragraph>
                  <Text strong>已使用空间: </Text>
                  <Text>
                    {`${((storageInfo.storage_used || storageInfo.used_space_mb || 0) / 1024).toFixed(2)} GB / ${((storageInfo.storage_capacity || storageInfo.total_space_mb || 1024) / 1024).toFixed(2)} GB`}
                  </Text>
                </Paragraph>
                <Progress 
                  percent={storageInfo.usage_percentage || 0} 
                  status={(storageInfo.usage_percentage || 0) > 90 ? "exception" : "normal"}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': (storageInfo.usage_percentage || 0) > 90 ? '#ff4d4f' : '#87d068',
                  }}
                />
                <Paragraph>
                  <Text type="secondary">
                    剩余可用空间: {`${((storageInfo.storage_free || 0) / 1024).toFixed(2)} GB`}
                  </Text>
                </Paragraph>
              </Space>
            </Card>
            
            {/* CDK激活卡片 */}
            <Card>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
                  <KeyOutlined style={{ fontSize: '24px', marginRight: '12px', color: '#52c41a' }} />
                  <Title level={4} style={{ margin: 0 }}>激活CDK</Title>
                </div>
                <Paragraph>
                  输入CDK激活码增加存储空间。默认CDK为"1"，可增加1GB存储空间。
                </Paragraph>
                <Form
                  form={cdkForm}
                  onFinish={handleActivateCDK}
                  layout="vertical"
                >
                  <Form.Item
                    name="cdk"
                    rules={[{ required: true, message: '请输入CDK' }]}
                  >
                    <Input placeholder="输入CDK激活码" />
                  </Form.Item>
                  <Form.Item>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      loading={cdkLoading}
                      icon={<KeyOutlined />}
                    >
                      激活
                    </Button>
                  </Form.Item>
                </Form>
              </Space>
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default Profile as React.ComponentType; 