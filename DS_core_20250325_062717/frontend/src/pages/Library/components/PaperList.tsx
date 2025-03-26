import React from 'react';
import { Table, Space, Button, Tooltip, Popconfirm, Upload, Tag, Typography } from 'antd';
import { 
  EditOutlined, DeleteOutlined, UploadOutlined, 
  CopyOutlined, DownloadOutlined
} from '@ant-design/icons';
import { Paper } from '../hooks/usePapers';
import { RcFile } from 'antd/es/upload';

const { Text } = Typography;

interface PaperListProps {
  papers: Paper[];
  loading: boolean;
  pdfUploading: boolean;
  downloadLoading: Record<number, boolean>;
  searchText: string;
  onRead: (doi: string) => void;
  onEdit: (paper: Paper) => void;
  onDelete: (id: number) => void;
  onPdfUpload: (id: number, file: RcFile) => void;
  onPdfDownload: (id: number) => void;
  onPdfDelete: (id: number) => void;
  getTranslation: (zhText: string, enText: string) => string;
}

const PaperList: React.FC<PaperListProps> = ({
  papers,
  loading,
  pdfUploading,
  downloadLoading,
  searchText,
  onRead,
  onEdit,
  onDelete,
  onPdfUpload,
  onPdfDownload,
  onPdfDelete,
  getTranslation
}) => {
  // 过滤论文
  const filteredPapers = papers.filter(paper => {
    if (!searchText) return true;
    const lowerSearchText = searchText.toLowerCase();
    
    return (
      paper.title.toLowerCase().includes(lowerSearchText) ||
      paper.authors.toLowerCase().includes(lowerSearchText) ||
      (paper.abstract || '').toLowerCase().includes(lowerSearchText) ||
      (paper.journal || '').toLowerCase().includes(lowerSearchText) ||
      (paper.doi || '').toLowerCase().includes(lowerSearchText)
    );
  });

  const columns = [
    {
      title: getTranslation('标题', 'Title'),
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Paper) => {
        return (
          <div>
            <div>{text}</div>
            <Text type="secondary" style={{ fontSize: '12px' }}>{record.authors}</Text>
            {record.doi && (
              <div>
                <Text type="secondary" style={{ fontSize: '12px' }}>DOI: {record.doi}</Text>
              </div>
            )}
          </div>
        );
      }
    },
    {
      title: getTranslation('期刊/年份', 'Journal/Year'),
      dataIndex: 'journal',
      key: 'journal',
      width: '20%',
      render: (text: string, record: Paper) => {
        return (
          <div>
            {text && <div>{text}</div>}
            <Tag color="blue">{record.year}</Tag>
          </div>
        );
      }
    },
    {
      title: getTranslation('操作', 'Actions'),
      key: 'action',
      width: '25%',
      render: (text: string, record: Paper) => (
        <Space size="small">
          {record.doi && (
            <Button 
              icon={<CopyOutlined />} 
              size="small"
              onClick={() => onRead(record.doi || '')}
            >
              {getTranslation('复制DOI', 'Copy DOI')}
            </Button>
          )}
          <Button 
            icon={<EditOutlined />} 
            size="small"
            onClick={() => onEdit(record)}
          >
            {getTranslation('编辑', 'Edit')}
          </Button>
          <Popconfirm
            title={getTranslation('确定删除这篇论文吗？', 'Are you sure to delete this paper?')}
            onConfirm={() => onDelete(record.id)}
            okText={getTranslation('是', 'Yes')}
            cancelText={getTranslation('否', 'No')}
          >
            <Button 
              danger 
              icon={<DeleteOutlined />}
              size="small"
            >
              {getTranslation('删除', 'Delete')}
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '8px' }}>
      <Table 
        dataSource={filteredPapers}
        columns={columns}
        rowKey="id"
        loading={loading}
        style={{ backgroundColor: 'white', borderRadius: '8px' }}
        pagination={{ 
          pageSize: 15,
          showTotal: (total) => getTranslation(`共 ${total} 篇文献`, `Total ${total} papers`)
        }}
      />
    </div>
  );
};

export default PaperList; 