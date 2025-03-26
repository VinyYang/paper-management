import React, { useState, useEffect } from 'react';
import { Card, Typography, Switch, Form, Button, Select, message, Divider, Radio, Space } from 'antd';
import { useSettings, ThemeType, LanguageType } from '../contexts/SettingsContext';
import { GlobalOutlined, BulbOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Option } = Select;

const Settings: React.FC = () => {
  const { themeMode, language, setThemeMode, setLanguage } = useSettings();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  
  // 组件加载时设置初始表单值
  useEffect(() => {
    form.setFieldsValue({
      theme: themeMode,
      language: language,
      autoDownload: localStorage.getItem('autoDownload') === 'true',
      notificationEnabled: localStorage.getItem('notificationEnabled') === 'true',
      pdfReader: localStorage.getItem('pdfReader') || 'embedded'
    });
  }, [form, themeMode, language]);

  const handleSubmit = (values: any) => {
    setLoading(true);
    console.log('设置已更新:', values);
    
    // 更新主题
    setThemeMode(values.theme as ThemeType);
    
    // 更新语言
    setLanguage(values.language as LanguageType);
    
    // 保存其他设置到localStorage
    localStorage.setItem('autoDownload', values.autoDownload.toString());
    localStorage.setItem('notificationEnabled', values.notificationEnabled.toString());
    localStorage.setItem('pdfReader', values.pdfReader);
    
    // 显示成功消息
    setTimeout(() => {
      setLoading(false);
      message.success(language === 'zh_CN' ? '设置已保存' : 'Settings saved');
    }, 500);
  };

  // 获取翻译文本
  const getTranslation = (zhText: string, enText: string) => {
    return language === 'zh_CN' ? zhText : enText;
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={3}>{getTranslation('系统设置', 'System Settings')}</Title>
        <Paragraph>
          {getTranslation('自定义应用程序设置和偏好。', 'Customize application settings and preferences.')}
        </Paragraph>
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            theme: themeMode,
            language: language,
            autoDownload: true,
            notificationEnabled: true,
            pdfReader: 'embedded'
          }}
          style={{ maxWidth: '600px' }}
        >
          <Divider orientation="left">
            {getTranslation('外观设置', 'Appearance Settings')}
          </Divider>
          
          <Form.Item 
            name="theme" 
            label={getTranslation('界面主题', 'Theme')}
          >
            <Radio.Group>
              <Space direction="vertical">
                <Radio.Button value="light">
                  <Space>
                    <BulbOutlined />
                    {getTranslation('浅色', 'Light')}
                  </Space>
                </Radio.Button>
                <Radio.Button value="dark">
                  <Space>
                    <BulbOutlined />
                    {getTranslation('深色', 'Dark')}
                  </Space>
                </Radio.Button>
                <Radio.Button value="system">
                  <Space>
                    <BulbOutlined />
                    {getTranslation('跟随系统', 'System')}
                  </Space>
                </Radio.Button>
              </Space>
            </Radio.Group>
          </Form.Item>
          
          <Form.Item 
            name="language" 
            label={getTranslation('语言', 'Language')}
          >
            <Radio.Group>
              <Radio.Button value="zh_CN">
                <Space>
                  <GlobalOutlined />
                  简体中文
                </Space>
              </Radio.Button>
              <Radio.Button value="en_US">
                <Space>
                  <GlobalOutlined />
                  English
                </Space>
              </Radio.Button>
            </Radio.Group>
          </Form.Item>
          
          <Divider orientation="left">
            {getTranslation('文献管理', 'Literature Management')}
          </Divider>
          
          <Form.Item 
            name="pdfReader" 
            label={getTranslation('PDF阅读器', 'PDF Reader')}
          >
            <Select>
              <Option value="embedded">{getTranslation('内嵌阅读器', 'Embedded Reader')}</Option>
              <Option value="external">{getTranslation('使用外部阅读器', 'External Reader')}</Option>
            </Select>
          </Form.Item>
          
          <Form.Item 
            name="autoDownload" 
            label={getTranslation('自动下载', 'Auto Download')} 
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Paragraph type="secondary" style={{ marginTop: -16 }}>
            {getTranslation('当使用DOI查找文献时自动尝试下载PDF', 'Automatically try to download PDF when searching by DOI')}
          </Paragraph>
          
          <Divider orientation="left">
            {getTranslation('通知设置', 'Notification Settings')}
          </Divider>
          
          <Form.Item 
            name="notificationEnabled" 
            label={getTranslation('启用通知', 'Enable Notifications')} 
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Paragraph type="secondary" style={{ marginTop: -16 }}>
            {getTranslation('接收新文献推荐和引用提醒', 'Receive new literature recommendations and citation alerts')}
          </Paragraph>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              {getTranslation('保存设置', 'Save Settings')}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings as React.ComponentType; 