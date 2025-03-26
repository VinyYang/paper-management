import React from 'react';
import { Card, Typography, Button, Space, Upload, Tooltip, Popconfirm, message, Tag, theme } from 'antd';
import { 
  EditOutlined, DeleteOutlined, 
  UploadOutlined, CopyOutlined 
} from '@ant-design/icons';
import { RcFile } from 'antd/es/upload';
import { Paper } from '../hooks/usePapers';

const { Text, Paragraph } = Typography;

interface PaperCardProps {
  paper: Paper;
  pdfUploading: boolean;
  onRead: (doi: string) => void;
  onEdit: (paper: Paper) => void;
  onDelete: (id: number) => void;
  onPdfUpload: (id: number, file: RcFile) => void;
  onPdfDelete: (id: number) => void;
  onCopyDoi: (doi: string) => void;
  getTranslation: (zhText: string, enText: string) => string;
}

const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  pdfUploading,
  onRead,
  onEdit,
  onDelete,
  onPdfUpload,
  onPdfDelete,
  onCopyDoi,
  getTranslation
}) => {
  const { token } = theme.useToken();
  
  const cardActions = (
    <Space key="actions" style={{ width: '100%', justifyContent: 'center' }}>
      {paper.doi && (
        <Button 
          type="text" 
          icon={<CopyOutlined />} 
          onClick={() => onRead(paper.doi || '')}
        >
          {getTranslation('复制DOI', 'Copy DOI')}
        </Button>
      )}
      <Button 
        type="text" 
        icon={<EditOutlined />} 
        onClick={() => onEdit(paper)}
      >
        {getTranslation('编辑', 'Edit')}
      </Button>
      <Popconfirm
        title={getTranslation('确定删除这篇论文吗？', 'Are you sure to delete this paper?')}
        onConfirm={() => onDelete(paper.id)}
        okText={getTranslation('是', 'Yes')}
        cancelText={getTranslation('否', 'No')}
      >
        <Button 
          type="text" 
          danger 
          icon={<DeleteOutlined />}
        >
          {getTranslation('删除', 'Delete')}
        </Button>
      </Popconfirm>
    </Space>
  );

  return (
    <div 
      style={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        border: `1px solid ${token.colorBorderSecondary}`,
        borderRadius: token.borderRadiusLG,
        overflow: 'hidden',
        transition: 'all 0.3s',
        boxShadow: token.boxShadowTertiary
      }}
      className="paper-card-container"
    >
      <Card 
        hoverable 
        className="paper-card"
        style={{ 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column',
          flex: 1,
          border: 'none',
          background: token.colorBgContainer
        }}
        bodyStyle={{ 
          flex: '1 0 auto',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        <Card.Meta
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1, marginRight: 16 }}>
                <Typography.Title level={5} style={{ margin: 0 }}>
                  {paper.title}
                </Typography.Title>
                <Typography.Text type="secondary">
                  {paper.authors || getTranslation('暂无作者', 'No authors')}
                </Typography.Text>
                {paper.doi && (
                  <div style={{ marginTop: 4 }}>
                    <Typography.Text type="secondary" copyable={{ text: paper.doi }}>
                      {getTranslation('DOI', 'DOI')}: {paper.doi}
                    </Typography.Text>
                  </div>
                )}
              </div>
              <Tag color="blue">{paper.year}</Tag>
            </div>
          }
          description={
            <div style={{ flex: '1 0 auto' }}>
              <Typography.Paragraph ellipsis={{ rows: 2 }}>
                {paper.abstract || getTranslation('暂无摘要', 'No abstract')}
              </Typography.Paragraph>
              {paper.journal && (
                <Typography.Text type="secondary">
                  {paper.journal}
                </Typography.Text>
              )}
            </div>
          }
        />
      </Card>
      
      {/* 固定在底部的操作栏 */}
      <div 
        style={{ 
          padding: '12px', 
          borderTop: `1px solid ${token.colorBorderSecondary}`,
          backgroundColor: token.colorBgContainer,
          display: 'flex',
          justifyContent: 'center',
          position: 'sticky',
          bottom: 0,
          width: '100%'
        }}
      >
        {cardActions}
      </div>
    </div>
  );
};

export default PaperCard; 