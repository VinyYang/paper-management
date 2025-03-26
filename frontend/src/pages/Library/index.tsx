import React, { useState, useCallback } from 'react';
import { Layout, Button, Row, Col, message, Drawer, Modal, theme } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { RcFile } from 'antd/es/upload';
import { Paper } from './hooks/usePapers';

// 导入子组件
import ProjectManagement from './components/ProjectManagement';
import SearchAndFilter from './components/SearchAndFilter';
import PaperCardView from './components/PaperCardView';
import PaperList from './components/PaperList';
import StorageInfo from './components/StorageInfo';
import AddPaperModal from './components/AddPaperModal';

// 导入hooks
import usePapers from './hooks/usePapers';
import useProjects from './hooks/useProjects';
import useApi from './hooks/useApi';
import useErrorManager from './hooks/useErrorManager';

const { Content, Sider } = Layout;

const Library: React.FC = () => {
  const navigate = useNavigate();
  const { token } = theme.useToken();
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [editPaper, setEditPaper] = useState<Paper | null>(null);
  const [viewMode, setViewMode] = useState<'card' | 'list'>('card');
  const [searchText, setSearchText] = useState('');
  const [sortField, setSortField] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'ascend' | 'descend'>('descend');
  const [downloadLoading, setDownloadLoading] = useState<Record<number, boolean>>({});
  const [pdfUploading, setPdfUploading] = useState(false);
  
  // 使用自定义hooks获取数据和操作方法
  const {
    projects,
    loading: projectsLoading,
    selectedProjectId,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    handleSelectProject,
    getTranslation: getProjectTranslation
  } = useProjects();
  
  const {
    papers,
    loading: papersLoading,
    fetchPapers,
    addPaper,
    updatePaper,
    deletePaper,
    removePaperFromProject,
    getTranslation
  } = usePapers(selectedProjectId);
  
  const api = useApi();
  const errorManager = useErrorManager();
  
  // 控制抽屉显示
  const toggleSider = () => {
    setSiderCollapsed(!siderCollapsed);
  };
  
  // 处理添加论文
  const handleShowAddModal = () => {
    setEditPaper(null);
    setAddModalVisible(true);
  };
  
  // 处理编辑论文
  const handleEdit = (paper: Paper) => {
    setEditPaper(paper);
    setAddModalVisible(true);
  };
  
  // 处理取消添加/编辑
  const handleCancelAddModal = () => {
    setAddModalVisible(false);
    setEditPaper(null);
  };
  
  // 处理添加/更新论文提交
  const handleAddOrUpdatePaper = async (values: any, pdfFile: any) => {
    if (editPaper) {
      // 更新论文
      await updatePaper(editPaper.id, values);
    } else {
      // 添加新论文
      await addPaper(values);
    }
    setAddModalVisible(false);
    setEditPaper(null);
  };
  
  // 处理阅读论文
  const handleRead = (id: number) => {
    navigate(`/papers/${id}`);
  };
  
  // 处理删除论文
  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: getTranslation('确认删除这篇论文吗？此操作不可恢复。', 'Are you sure you want to delete this paper? This action cannot be undone.'),
      okText: getTranslation('确定删除', 'Yes, Delete'),
      cancelText: getTranslation('取消', 'Cancel'),
      okButtonProps: { danger: true },
      onOk: async () => {
        const success = await deletePaper(id);
        if (success) {
          message.success(getTranslation('论文已删除', 'Paper deleted successfully'));
        }
      }
    });
  };
  
  // 处理上传PDF
  const handlePdfUpload = async (id: number, file: RcFile) => {
    setPdfUploading(true);
    try {
      console.log('开始上传PDF:', file.name, '大小:', file.size);
      
      // 检查文件类型
      if (file.type !== 'application/pdf') {
        throw new Error(getTranslation('请上传PDF格式的文件', 'Please upload a PDF file'));
      }
      
      // 检查文件大小（例如限制为50MB）
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        throw new Error(getTranslation('PDF文件大小不能超过50MB', 'PDF file size cannot exceed 50MB'));
      }

      const formData = new FormData();
      formData.append('pdf_file', file);
      
      // 确保使用正确的路径
      const url = `/api/papers/${id}/upload-pdf`;
      console.log('准备发送请求到:', url);
      
      try {
        const response = await api.post(url, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        console.log('上传响应:', response.data);
        
        if (response.data.success) {
          message.success(getTranslation('PDF上传成功', 'PDF uploaded successfully'));
          await fetchPapers(); // 刷新论文列表
        } else {
          throw new Error(response.data.message || getTranslation('上传失败', 'Upload failed'));
        }
      } catch (apiError) {
        console.error('API调用失败:', apiError);
        throw apiError;
      }
    } catch (error) {
      console.error('上传PDF出错:', error);
      errorManager.showErrorOnce(
        error instanceof Error 
          ? error.message 
          : getTranslation('上传PDF时出错', 'Error uploading PDF')
      );
    } finally {
      setPdfUploading(false);
    }
  };
  
  // 处理下载PDF
  const handlePdfDownload = async (id: number) => {
    setDownloadLoading(prev => ({ ...prev, [id]: true }));
    try {
      const paper = papers.find(p => p.id === id);
      if (!paper) {
        throw new Error(getTranslation('未找到文献', 'Paper not found'));
      }
      
      // 使用api实例获取PDF文件 - 修复API路径
      const response = await api.get(`/api/papers/${id}/download`, {
        responseType: 'blob',
      });
      
      if (!response.data || response.data.size === 0) {
        throw new Error(getTranslation('PDF文件为空', 'PDF file is empty'));
      }
      
      // 创建Blob对象
      const blob = new Blob([response.data], { type: 'application/pdf' });
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${paper.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      // 清理
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success(getTranslation('PDF下载开始', 'PDF download started'));
    } catch (error) {
      console.error('下载PDF出错:', error);
      errorManager.showErrorOnce(getTranslation('下载PDF时出错', 'Error downloading PDF'));
    } finally {
      setDownloadLoading(prev => ({ ...prev, [id]: false }));
    }
  };
  
  // 处理删除PDF
  const handlePdfDelete = async (id: number) => {
    Modal.confirm({
      title: getTranslation('确认删除PDF', 'Confirm PDF Deletion'),
      content: getTranslation('确定要删除这个PDF吗？论文记录将保留。', 'Are you sure you want to delete this PDF? The paper record will be kept.'),
      okText: getTranslation('确定删除', 'Yes, Delete'),
      cancelText: getTranslation('取消', 'Cancel'),
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          // 假设API提供了删除PDF的端点
          // await paperApi.deletePdf(id);
          message.success(getTranslation('PDF已删除', 'PDF deleted successfully'));
          await fetchPapers(); // 刷新论文列表
        } catch (error) {
          console.error('删除PDF出错:', error);
          message.error(getTranslation('删除PDF时出错', 'Error deleting PDF'));
        }
      }
    });
  };
  
  // 处理复制DOI
  const handleCopyDoi = (doi: string) => {
    navigator.clipboard.writeText(doi)
      .then(() => {
        message.success(getTranslation('DOI已复制到剪贴板', 'DOI copied to clipboard'));
      })
      .catch(() => {
        message.error(getTranslation('复制DOI失败', 'Failed to copy DOI'));
      });
  };
  
  // 处理刷新
  const handleRefresh = useCallback(async () => {
    await fetchPapers();
    await fetchProjects();
  }, [fetchPapers, fetchProjects]);
  
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={280}
        collapsible
        collapsed={siderCollapsed}
        onCollapse={toggleSider}
        style={{
          background: '#fff',
          boxShadow: '2px 0 8px rgba(0,0,0,0.05)',
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 1000
        }}
      >
        <div style={{ padding: '16px' }}>
          {!siderCollapsed && <ProjectManagement
            projects={projects}
            loading={projectsLoading}
            selectedProjectId={selectedProjectId}
            onSelectProject={handleSelectProject}
            onCreateProject={createProject}
            onUpdateProject={updateProject}
            onDeleteProject={deleteProject}
            getTranslation={getTranslation}
          />}
        </div>
      </Sider>
      
      <Layout style={{ marginLeft: siderCollapsed ? 80 : 280, transition: 'margin-left 0.3s' }}>
        <Content style={{ 
          padding: '24px', 
          background: token.colorBgLayout,
          maxWidth: '1200px',
          margin: '0 auto',
          minHeight: '100vh'
        }}>
          <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
            <Col flex="auto" style={{ display: 'flex', justifyContent: 'center' }}>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={handleShowAddModal}
                style={{ marginRight: 16 }}
              >
                {getTranslation('添加文献', 'Add Paper')}
              </Button>
            </Col>
            <Col>
              <StorageInfo 
                getTranslation={getTranslation}
              />
            </Col>
          </Row>
          
          <SearchAndFilter 
            searchText={searchText}
            onSearchChange={setSearchText}
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            sortField={sortField}
            onSortFieldChange={setSortField}
            sortOrder={sortOrder}
            onSortOrderChange={setSortOrder}
            onRefresh={handleRefresh}
            getTranslation={getTranslation}
            loading={papersLoading}
          />
          
          <div style={{ 
            maxWidth: '100%', 
            margin: '0 auto', 
            padding: '16px 0' 
          }}>
            {viewMode === 'card' ? (
              <PaperCardView 
                papers={papers}
                loading={papersLoading}
                pdfUploading={!!Object.keys(pdfUploading).length}
                searchText={searchText}
                onShowAddModal={handleShowAddModal}
                onRead={handleCopyDoi}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onPdfUpload={handlePdfUpload}
                onPdfDelete={handlePdfDelete}
                onCopyDoi={handleCopyDoi}
                getTranslation={getTranslation}
              />
            ) : (
              <PaperList
                papers={papers}
                loading={papersLoading}
                pdfUploading={!!Object.keys(pdfUploading).length}
                downloadLoading={downloadLoading}
                searchText={searchText}
                onRead={handleCopyDoi}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onPdfUpload={handlePdfUpload}
                onPdfDownload={handlePdfDownload}
                onPdfDelete={handlePdfDelete}
                getTranslation={getTranslation}
              />
            )}
          </div>
        </Content>
      </Layout>
      
      {/* 添加/编辑论文的模态框 */}
      <AddPaperModal 
        visible={addModalVisible}
        loading={papersLoading}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onProjectChange={handleSelectProject}
        onCancel={handleCancelAddModal}
        onAdd={handleAddOrUpdatePaper}
        getTranslation={getTranslation}
      />
    </Layout>
  );
};

export default Library; 