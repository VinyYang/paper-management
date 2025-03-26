import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { List, Button, Modal, message, Space, Typography, Divider, Tooltip, Tabs, Input, Table } from 'antd';
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined, EditOutlined, CopyOutlined, SearchOutlined } from '@ant-design/icons';
import { projectApi, paperApi, errorManager } from '../services/api';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  papers?: Paper[];
}

interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract: string;
  doi: string;
  created_at: string;
  journal?: string;
  year?: string;
}

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [addPaperModalVisible, setAddPaperModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Paper[]>([]);
  const [allPapers, setAllPapers] = useState<Paper[]>([]);
  const [allPapersLoading, setAllPapersLoading] = useState(false);
  const [librarySearchQuery, setLibrarySearchQuery] = useState('');

  const fetchProject = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await projectApi.getProject(parseInt(id));
      console.log('项目详情响应:', response);
      setProject(response);
      setPapers(response.papers || []);
    } catch (error) {
      console.error('获取项目详情失败:', error);
      errorManager.showErrorOnce('获取项目详情失败');
    } finally {
      setLoading(false);
    }
  }, [id]);

  // 获取所有论文
  const fetchAllPapers = async () => {
    try {
      setAllPapersLoading(true);
      const response = await paperApi.getPapers();
      console.log('获取到的论文列表:', response);
      if (response && response.data) {
        // 过滤掉已经在项目中的论文
        const projectPaperIds = papers.map(paper => paper.id);
        const filteredPapers = response.data.filter((paper: Paper) => 
          !projectPaperIds.includes(paper.id)
        );
        setAllPapers(filteredPapers);
      } else {
        setAllPapers([]);
      }
    } catch (error) {
      console.error('获取论文列表失败:', error);
      errorManager.showErrorOnce('获取论文列表失败');
    } finally {
      setAllPapersLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchProject();
  }, [id]);

  // 当打开添加论文对话框时，获取现有论文列表
  useEffect(() => {
    if (addPaperModalVisible) {
      fetchAllPapers();
    }
  }, [addPaperModalVisible, papers]);

  const handleSearchPapers = async () => {
    if (!searchQuery) return;
    try {
      // 搜索文献，仅获取元数据
      const response = await paperApi.searchByDoi(searchQuery);
      if (response.data) {
        setSearchResults([response.data]);
      } else {
        message.info('未找到相关文献信息');
        setSearchResults([]);
      }
    } catch (error) {
      console.error('搜索文献失败:', error);
      errorManager.showErrorOnce('搜索文献失败');
      setSearchResults([]);
    }
  };

  const handleAddPaper = async (paperId: number) => {
    if (!id) return;
    try {
      message.loading({ content: '正在添加文献...', key: 'addingPaper' });
      
      // 添加论文到项目
      await projectApi.addPaper(parseInt(id), paperId);
      
      // 关闭对话框
      setAddPaperModalVisible(false);
      
      // 显示成功消息
      message.success({ content: '添加文献成功', key: 'addingPaper', duration: 2 });
      
      // 刷新项目详情和论文列表
      await fetchProject();
      
      // 延迟一点时间后再次刷新，确保后端数据已更新
      setTimeout(async () => {
        await fetchProject();
        await fetchAllPapers();
        console.log("项目和论文数据已刷新");
      }, 500);
    } catch (error) {
      console.error('添加文献失败:', error);
      message.error({
        content: error instanceof Error 
          ? `添加文献失败: ${error.message}`
          : '添加文献失败，请稍后重试',
        key: 'addingPaper',
        duration: 3
      });
    }
  };

  const handleRemovePaper = async (paperId: number) => {
    if (!id) return;
    try {
      await projectApi.removePaper(parseInt(id), paperId);
      message.success('移除文献成功');
      fetchProject();
    } catch (error) {
      errorManager.showErrorOnce('移除文献失败');
    }
  };

  const handleEditPaper = (paperId: number) => {
    // 导航到库页面并通过查询参数指示要编辑的论文
    navigate(`/library?edit=${paperId}`);
  };

  // 过滤库中已有的论文
  const filteredLibraryPapers = allPapers.filter(paper => {
    if (!librarySearchQuery) return true;
    const query = librarySearchQuery.toLowerCase();
    return (
      paper.title.toLowerCase().includes(query) ||
      paper.authors.toLowerCase().includes(query) ||
      (paper.doi && paper.doi.toLowerCase().includes(query)) ||
      (paper.journal && paper.journal.toLowerCase().includes(query))
    );
  });

  if (!project) {
    return <div>加载中...</div>;
  }

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/projects')}>
            返回项目列表
          </Button>
          <Title level={2}>{project.name}</Title>
          <Button type="default" onClick={() => fetchProject()} style={{ marginLeft: 'auto' }}>
            刷新数据
          </Button>
        </Space>

        <Paragraph>{project.description}</Paragraph>
        <Divider />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <Title level={3}>项目文献</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddPaperModalVisible(true)}>
            添加文献
          </Button>
        </div>

        <List
          loading={loading}
          dataSource={papers}
          renderItem={(paper) => (
            <List.Item
              key={paper.id}
              actions={[
                <Button 
                  icon={<EditOutlined />} 
                  onClick={() => handleEditPaper(paper.id)}
                >
                  编辑
                </Button>,
                <Button 
                  danger 
                  icon={<DeleteOutlined />} 
                  onClick={() => handleRemovePaper(paper.id)}
                >
                  移除
                </Button>
              ]}
            >
              <List.Item.Meta
                title={<strong>{paper.title}</strong>}
                description={
                  <div>
                    <div>作者: {paper.authors}</div>
                    {paper.journal && <div>期刊: {paper.journal}</div>}
                    {paper.year && <div>年份: {paper.year}</div>}
                    {paper.doi && (
                      <div>
                        DOI: {paper.doi}
                        <Tooltip title="复制DOI">
                          <Button 
                            type="text" 
                            size="small" 
                            icon={<CopyOutlined />} 
                            onClick={(e) => {
                              e.stopPropagation();
                              navigator.clipboard.writeText(paper.doi);
                              message.success('DOI已复制到剪贴板');
                            }}
                            style={{ marginLeft: 8 }}
                          />
                        </Tooltip>
                      </div>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Space>

      <Modal
        title="添加文献"
        open={addPaperModalVisible}
        onCancel={() => setAddPaperModalVisible(false)}
        width={800}
        footer={null}
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="DOI搜索" key="1">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="输入 DOI 搜索文献"
                  style={{ width: '300px' }}
                />
                <Button type="primary" onClick={handleSearchPapers}>
                  搜索
                </Button>
              </Space>

              <List
                dataSource={searchResults}
                renderItem={(paper) => (
                  <List.Item
                    actions={[
                      <Button
                        key="add"
                        type="primary"
                        onClick={() => handleAddPaper(paper.id)}
                      >
                        添加
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      title={paper.title}
                      description={
                        <Space direction="vertical">
                          <div>作者：{paper.authors}</div>
                          <div>
                            DOI：{paper.doi}
                            <Tooltip title="复制DOI">
                              <Button 
                                type="text" 
                                size="small" 
                                icon={<CopyOutlined />} 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigator.clipboard.writeText(paper.doi);
                                  message.success('DOI已复制到剪贴板');
                                }}
                                style={{ marginLeft: 8 }}
                              />
                            </Tooltip>
                          </div>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </Space>
          </TabPane>
          <TabPane tab="浏览文献库" key="2">
            <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
              <Input 
                placeholder="搜索文献库"
                prefix={<SearchOutlined />}
                value={librarySearchQuery}
                onChange={(e) => setLibrarySearchQuery(e.target.value)}
                style={{ marginBottom: 16 }}
              />
              <Table
                dataSource={filteredLibraryPapers}
                loading={allPapersLoading}
                rowKey="id"
                pagination={{ pageSize: 5 }}
                columns={[
                  {
                    title: '标题',
                    dataIndex: 'title',
                    key: 'title',
                    ellipsis: true,
                  },
                  {
                    title: '作者',
                    dataIndex: 'authors',
                    key: 'authors',
                    ellipsis: true,
                  },
                  {
                    title: '期刊',
                    dataIndex: 'journal',
                    key: 'journal',
                    ellipsis: true,
                  },
                  {
                    title: '操作',
                    key: 'action',
                    render: (_, record) => (
                      <Button 
                        type="primary" 
                        size="small"
                        onClick={() => handleAddPaper(record.id)}
                      >
                        添加到项目
                      </Button>
                    ),
                  },
                ]}
              />
            </Space>
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
};

export default ProjectDetail as React.ComponentType; 