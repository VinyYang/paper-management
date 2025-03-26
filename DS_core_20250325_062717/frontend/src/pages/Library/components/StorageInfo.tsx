import React from 'react';
import { Button, Popover, Typography, Progress } from 'antd';
import { CloudUploadOutlined } from '@ant-design/icons';

const { Paragraph, Text } = Typography;

interface StorageInfoProps {
  storageInfo?: {
    storage_capacity: number;
    storage_used: number;
    storage_free: number;
    usage_percentage: number;
    used_space_mb?: number;
    total_space_mb?: number;
  } | null;
  getTranslation: (zhText: string, enText: string) => string;
}

const StorageInfo: React.FC<StorageInfoProps> = ({
  storageInfo,
  getTranslation
}) => {
  if (!storageInfo) {
    return (
      <Button icon={<CloudUploadOutlined />} disabled>
        {getTranslation('存储空间', 'Storage')}
      </Button>
    );
  }

  return (
    <Popover
      content={
        <div style={{ width: 250 }}>
          <Paragraph>
            <Text strong>{getTranslation('已使用空间:', 'Used Space:')}</Text>
            <Text> {((storageInfo?.storage_used || storageInfo?.used_space_mb || 0) / 1024).toFixed(2)} GB / {((storageInfo?.storage_capacity || storageInfo?.total_space_mb || 1024) / 1024).toFixed(2)} GB</Text>
          </Paragraph>
          <Progress 
            percent={storageInfo?.usage_percentage} 
            status={((storageInfo?.usage_percentage) ?? 0) > 90 ? "exception" : "normal"}
            strokeColor={{
              '0%': '#108ee9',
              '100%': ((storageInfo?.usage_percentage) ?? 0) > 90 ? '#ff4d4f' : '#87d068',
            }}
          />
          <Paragraph>
            <Text type="secondary">{getTranslation('剩余空间:', 'Free Space:')} {((storageInfo?.storage_free || 0) / 1024).toFixed(2)} GB</Text>
          </Paragraph>
        </div>
      }
      title={getTranslation('存储空间', 'Storage Space')}
      trigger="hover"
      placement="bottomRight"
    >
      <Button icon={<CloudUploadOutlined />}>
        {getTranslation('存储信息', 'Storage Info')}
      </Button>
    </Popover>
  );
};

export default StorageInfo; 