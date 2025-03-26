import React from 'react';
import { Button, theme, Row, Col, Spin, Empty } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Paper } from '../hooks/usePapers';
import PaperCard from './PaperCard';
import { RcFile } from 'antd/es/upload';

interface PaperCardViewProps {
  papers: Paper[];
  loading: boolean;
  pdfUploading: boolean;
  searchText: string;
  onShowAddModal: () => void;
  onRead: (doi: string) => void;
  onEdit: (paper: Paper) => void;
  onDelete: (id: number) => void;
  onPdfUpload: (id: number, file: RcFile) => void;
  onPdfDelete: (id: number) => void;
  onCopyDoi: (doi: string) => void;
  getTranslation: (zhText: string, enText: string) => string;
}

const PaperCardView: React.FC<PaperCardViewProps> = ({
  papers,
  loading,
  pdfUploading,
  searchText,
  onShowAddModal,
  onRead,
  onEdit,
  onDelete,
  onPdfUpload,
  onPdfDelete,
  onCopyDoi,
  getTranslation
}) => {
  const { token } = theme.useToken();

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

  return (
    <div>
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
        </div>
      ) : filteredPapers.length === 0 ? (
        <Empty 
          description={
            searchText 
              ? getTranslation('未找到匹配的文献', 'No matching papers found') 
              : getTranslation('暂无文献记录', 'No papers yet')
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={onShowAddModal}
          >
            {getTranslation('添加文献', 'Add Paper')}
          </Button>
        </Empty>
      ) : (
        <Row gutter={[24, 24]}>
          {filteredPapers.map(paper => (
            <Col key={paper.id} xs={24} sm={12} md={8} lg={8} xl={6} xxl={6}>
              <PaperCard
                paper={paper}
                pdfUploading={pdfUploading}
                onRead={onRead}
                onEdit={onEdit}
                onDelete={onDelete}
                onPdfUpload={onPdfUpload}
                onPdfDelete={onPdfDelete}
                onCopyDoi={onCopyDoi}
                getTranslation={getTranslation}
              />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default PaperCardView; 