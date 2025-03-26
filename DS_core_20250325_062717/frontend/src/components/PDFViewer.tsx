import React from 'react';
import { Alert } from 'antd';

interface PDFViewerProps {
  file?: string;
  width?: number;
  onPageChange?: (page: number) => void;
}

const PDFViewer: React.FC<PDFViewerProps> = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <Alert
        message="PDF阅读功能已禁用"
        description="系统当前不支持PDF文件的查看和存储功能。"
        type="info"
        showIcon
      />
    </div>
  );
};

export default PDFViewer; 