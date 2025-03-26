import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useSettings } from '../contexts/SettingsContext';

const PaperReader: React.FC = () => {
  const navigate = useNavigate();
  const { language } = useSettings();
  
  // 翻译函数
  const getTranslation = (zhText: string, enText: string) => {
    return language === 'zh_CN' ? zhText : enText;
  };
  
  return (
    <div style={{ padding: '24px', height: '100%' }}>
      <Result
        status="info"
        title={getTranslation('PDF阅读功能已禁用', 'PDF Reading Feature Disabled')}
        subTitle={getTranslation(
          '系统当前不支持查看或存储PDF文件，仅支持管理论文元数据。', 
          'The system currently does not support viewing or storing PDF files. Only paper metadata management is supported.'
        )}
        extra={
          <Button 
            type="primary" 
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
          >
            {getTranslation('返回', 'Go Back')}
          </Button>
        }
      />
    </div>
  );
};

export default PaperReader; 