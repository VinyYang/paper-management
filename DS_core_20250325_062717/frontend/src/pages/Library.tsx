import React, { useState, useEffect } from 'react';
import { 
  Card, Typography, Button, Table, Space, Modal, Form, Input, message, Tooltip, Radio, theme, Row, Col, Select, Divider, Tag
} from 'antd';
import { 
  PlusOutlined, DeleteOutlined, EditOutlined, UnorderedListOutlined, AppstoreOutlined, CopyOutlined,
  SearchOutlined, ReadOutlined, FilterOutlined
} from '@ant-design/icons';
import { paperApi, projectApi, errorManager } from '../services/api';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSettings } from '../contexts/SettingsContext';

const { Title, Paragraph, Text } = Typography;
const { confirm } = Modal;

// 项目接口定义
interface Project {
  id: number;
  title: string;
  name?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  user_id?: number;
}

interface Paper {
  id: number;
  title: string;
  authors: string;
  journal?: string;
  year?: number;
  doi?: string;
  keywords?: string[];
  abstract?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
  reading_time?: number;
  last_read?: string;
  project_id?: number;
}

const Library: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { language } = useSettings();
  const { token } = theme.useToken();
  const [searchText, setSearchText] = useState<string>('');
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [editVisible, setEditVisible] = useState<boolean>(false);
  const [editFormVisible, setEditFormVisible] = useState<boolean>(false);
  const [currentPaper, setCurrentPaper] = useState<Paper | null>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const [displayMode, setDisplayMode] = useState<'list' | 'card'>('list');
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [isProjectModalVisible, setIsProjectModalVisible] = useState<boolean>(false);
  const [projectForm] = Form.useForm();
  
  // 项目过滤功能
  const [projectFilter, setProjectFilter] = useState<number | null>(null);

  // 翻译函数
  const getTranslation = (zhText: string, enText: string) => {
    return language === 'zh_CN' ? zhText : enText;
  };

  // 获取论文列表
  const fetchPapers = async () => {
    setLoading(true);
    try {
      const response = await paperApi.getPapers();
      if (response && response.data) {
        console.log('获取到的论文数据:', response.data);
        setPapers(response.data);
      }
    } catch (error) {
      console.error('获取论文列表失败:', error);
      errorManager.handleError(error, '获取论文列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取项目列表
  const fetchProjects = async () => {
    try {
      const response = await projectApi.getProjects();
      if (response && response.data) {
        console.log("获取到的项目列表:", response.data);
        setProjects(response.data);
      } else if (Array.isArray(response)) {
        console.log("获取到的项目列表(数组):", response);
        setProjects(response);
      } else {
        console.log("获取到的原始项目数据:", response);
        // 尝试从不同格式中提取项目数据
        if (response && typeof response === 'object') {
          setProjects([response]);
        } else {
          console.error("无法解析项目数据");
          setProjects([]);
        }
      }
    } catch (error) {
      console.error('获取项目列表失败', error);
      errorManager.handleError(error, '获取项目列表失败');
    }
  };

  // 创建项目
  const handleCreateProject = async (values: any) => {
    try {
      // 使用name字段而不是title字段，符合后端API要求
      const response = await projectApi.createProject({ name: values.name });
      console.log("创建项目响应:", response);
      await fetchProjects(); // 刷新项目列表
      messageApi.success(getTranslation('创建项目成功', 'Project created successfully'));
      setIsProjectModalVisible(false);
      projectForm.resetFields();
      
      // 如果是从添加/编辑论文对话框中创建的，则在创建后自动选择新创建的项目
      if (isModalVisible && form) {
        form.setFieldsValue({ project_id: String(response.id) });
      }
      if (editFormVisible && editForm) {
        editForm.setFieldsValue({ project_id: String(response.id) });
      }
    } catch (error) {
      errorManager.handleError(error, getTranslation('创建项目失败', 'Failed to create project'));
    }
  };

  // 组件加载时获取论文列表
  useEffect(() => {
    fetchPapers();
    fetchProjects();
    
    // 检查 URL 查询参数
    const searchParams = new URLSearchParams(location.search);
    
    // 检查是否包含要编辑的论文 ID
    const editPaperId = searchParams.get('edit');
    
    if (editPaperId) {
      console.log('检测到编辑参数:', editPaperId);
      // 查找要编辑的论文
      const paperId = parseInt(editPaperId);
      
      // 获取论文详细信息并打开编辑对话框
      const fetchPaperForEdit = async () => {
        try {
          const response = await paperApi.getPaper(paperId);
          if (response && response.data) {
            console.log('获取到编辑论文数据:', response.data);
            // 先设置当前论文
            setCurrentPaper(response.data);
            // 设置表单值
            editForm.setFieldsValue({
              title: response.data.title,
              authors: response.data.authors,
              journal: response.data.journal,
              year: response.data.year,
              doi: response.data.doi,
              abstract: response.data.abstract,
              project_id: response.data.project_id ? String(response.data.project_id) : "null",
            });
            // 直接显示编辑表单，而不是通过 handleEdit 函数
            setEditVisible(false);
            setEditFormVisible(true);
          }
        } catch (error) {
          console.error('获取论文详情失败:', error);
          errorManager.handleError(error, getTranslation('获取论文详情失败', 'Failed to get paper details'));
        }
      };
      
      fetchPaperForEdit();
    }
    
    // 检查是否包含项目过滤参数
    const projectIdParam = searchParams.get('project_id');
    if (projectIdParam) {
      const projectId = parseInt(projectIdParam);
      console.log('检测到项目过滤参数:', projectId);
      // 设置项目过滤器
      setProjectFilter(projectId);
    }
  }, [location.search, editForm]);

  // 当添加或编辑论文对话框打开时重新获取项目列表
  useEffect(() => {
    if (isModalVisible || editFormVisible) {
      console.log("对话框打开，获取项目列表");
      fetchProjects();
    }
  }, [isModalVisible, editFormVisible]);

  // 根据搜索条件和项目过滤论文
  const filteredPapers = papers.filter(paper => {
    // 项目过滤
    if (projectFilter !== null) {
      console.log(`正在过滤项目 ${projectFilter}, 论文项目ID: ${paper.project_id}`);
      if (paper.project_id !== projectFilter) {
        return false;
      }
    }
    
    // 搜索过滤
    if (!searchText) return true;
    const lowerSearchText = searchText.toLowerCase();
    return (
      (paper.title && paper.title.toLowerCase().includes(lowerSearchText)) ||
      (paper.authors && paper.authors.toLowerCase().includes(lowerSearchText)) ||
      (paper.journal && paper.journal.toLowerCase().includes(lowerSearchText)) ||
      (paper.abstract && paper.abstract.toLowerCase().includes(lowerSearchText)) ||
      (paper.doi && paper.doi.toLowerCase().includes(lowerSearchText)) ||
      (paper.year && paper.year.toString().includes(lowerSearchText))
    );
  });

  // 删除论文
  const handleDelete = async (id: number) => {
    confirm({
      title: getTranslation('确定要删除这篇论文吗?', 'Are you sure you want to delete this paper?'),
      content: getTranslation('删除后无法恢复', 'This action cannot be undone.'),
      okText: getTranslation('确定', 'Yes'),
      okType: 'danger',
      cancelText: getTranslation('取消', 'No'),
      async onOk() {
        try {
          await paperApi.deletePaper(id);
          messageApi.success(getTranslation('删除成功', 'Deleted successfully'));
          fetchPapers(); // 刷新列表
        } catch (error) {
          errorManager.handleError(error, getTranslation('删除失败', 'Failed to delete'));
        }
      },
    });
  };

  // 添加论文
  const handleAddPaper = async (values: any) => {
    // 处理project_id为null的情况
    const dataToSubmit = {
      ...values,
      project_id: values.project_id === "null" ? null : Number(values.project_id)
    };

    try {
      const response = await paperApi.createPaper(dataToSubmit);
      console.log('添加论文响应:', response);
      setIsModalVisible(false);
      form.resetFields();
      messageApi.success(getTranslation('添加成功', 'Added successfully'));
      
      // 延迟后多次刷新，确保数据同步
      fetchPapers();
      fetchProjects();
      
      setTimeout(() => {
        fetchPapers();
      }, 500);
    } catch (error) {
      errorManager.handleError(error, getTranslation('添加失败', 'Failed to add'));
    }
  };

  // 查看论文详情
  const handleViewPaper = (record: Paper) => {
    setCurrentPaper(record);
    // 设置表单为只读
    editForm.setFieldsValue({
      title: record.title,
      authors: record.authors,
      journal: record.journal,
      year: record.year,
      doi: record.doi,
      abstract: record.abstract,
      project_id: record.project_id ? String(record.project_id) : "null",
    });
    setEditVisible(true);
  };

  // 编辑论文
  const handleEdit = (record: Paper) => {
    console.log('handleEdit 被调用，论文数据:', record);
    setCurrentPaper(record);
    editForm.setFieldsValue({
      title: record.title,
      authors: record.authors,
      journal: record.journal,
      year: record.year,
      doi: record.doi,
      abstract: record.abstract,
      project_id: record.project_id ? String(record.project_id) : "null",
    });
    setEditVisible(false); // 关闭查看对话框
    setEditFormVisible(true); // 打开编辑对话框
    
    // 不要在这里清除URL参数，应该在编辑完成后再清除
  };

  // 提交编辑
  const handleEditSubmit = async (values: any) => {
    if (!currentPaper) return;
    console.log('handleEditSubmit 被调用，表单数据:', values);

    // 处理project_id为null的情况
    const dataToSubmit = {
      ...values,
      project_id: values.project_id === "null" ? null : Number(values.project_id)
    };

    try {
      await paperApi.updatePaper(currentPaper.id, dataToSubmit);
      setEditFormVisible(false);
      messageApi.success(getTranslation('更新成功', 'Updated successfully'));

      // 判断是否修改了project_id
      const projectChanged = currentPaper.project_id !== dataToSubmit.project_id;
      
      // 如果修改了项目关联
      if (projectChanged) {
        console.log(`论文项目关联已修改: 从 ${currentPaper.project_id} 到 ${dataToSubmit.project_id}`);
      }
      
      // 刷新论文列表
      fetchPapers();
      
      // 如果是从URL参数进入，编辑完成后清除URL参数
      if (location.search.includes('edit=')) {
        console.log('编辑完成，清除URL参数');
        // 使用setTimeout确保状态更新后再清除URL参数
        setTimeout(() => {
          navigate('/library', { replace: true });
        }, 100);
      }
    } catch (error) {
      errorManager.handleError(error, getTranslation('更新失败', 'Failed to update'));
    }
  };

  // 复制DOI
  const handleCopyDoi = (doi: string) => {
    navigator.clipboard.writeText(doi)
      .then(() => messageApi.success(getTranslation('DOI已复制', 'DOI copied')))
      .catch(() => messageApi.error(getTranslation('复制失败', 'Copy failed')));
  };

  // 渲染列表模式
  const renderTableMode = () => {
    const columns = [
      {
        title: getTranslation('标题', 'Title'),
        dataIndex: 'title',
        key: 'title',
        render: (text: string, record: Paper) => (
          <a onClick={() => handleViewPaper(record)}>
            {text}
          </a>
        ),
      },
      {
        title: getTranslation('作者', 'Authors'),
        dataIndex: 'authors',
        key: 'authors',
        width: 250,
      },
      {
        title: getTranslation('期刊', 'Journal'),
        dataIndex: 'journal',
        key: 'journal',
        width: 200,
      },
      {
        title: getTranslation('年份', 'Year'),
        dataIndex: 'year',
        key: 'year',
        width: 100,
      },
      {
        title: 'DOI',
        dataIndex: 'doi',
        key: 'doi',
        width: 150,
        render: (text: string) => text ? (
          <div className="doi-column">
            <span className="doi-text">{text}</span>
            <Tooltip title={getTranslation('复制DOI', 'Copy DOI')}>
              <CopyOutlined className="doi-copy-icon" onClick={() => handleCopyDoi(text)} />
            </Tooltip>
          </div>
        ) : null,
      },
      {
        title: getTranslation('项目', 'Project'),
        dataIndex: 'project_id',
        key: 'project_id',
        width: 150,
        render: (projectId: number) => projectId ? (
          <Tag 
            color="blue" 
            onClick={() => setProjectFilter(projectId)}
            style={{ cursor: 'pointer' }}
          >
            {projects.find(p => p.id === projectId)?.name || 
            projects.find(p => p.id === projectId)?.title || 
            `${getTranslation('项目', 'Project')} #${projectId}`}
          </Tag>
        ) : getTranslation('无', 'None'),
      },
      {
        title: getTranslation('操作', 'Actions'),
        key: 'action',
        width: 160,
        render: (_: any, record: Paper) => (
          <Space size="small">
            <Button 
              size="small" 
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              {getTranslation('编辑', 'Edit')}
            </Button>
            <Button 
              danger 
              size="small" 
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
            >
              {getTranslation('删除', 'Delete')}
            </Button>
          </Space>
        ),
      },
    ];

    return (
      <Table 
        dataSource={filteredPapers} 
        columns={columns} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
        locale={{
          emptyText: getTranslation('暂无数据', 'No Data')
        }}
      />
    );
  };

  // 渲染卡片模式
  const renderCardMode = () => {
    return (
      <Row gutter={[16, 16]} style={{ width: '100%' }}>
        {filteredPapers.map(paper => (
          <Col xs={24} sm={12} md={8} lg={6} key={paper.id}>
            <Card 
              hoverable
              title={
                <Tooltip title={paper.title}>
                  <div 
                    style={{ 
                      maxWidth: '100%', 
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      cursor: 'pointer'
                    }}
                    onClick={() => handleViewPaper(paper)}
                  >
                    {paper.title}
                  </div>
                </Tooltip>
              }
              actions={[
                <Tooltip title={getTranslation('编辑', 'Edit')}>
                  <EditOutlined key="edit" onClick={() => handleEdit(paper)} />
                </Tooltip>,
                <Tooltip title={getTranslation('删除', 'Delete')}>
                  <DeleteOutlined key="delete" onClick={() => handleDelete(paper.id)} />
                </Tooltip>,
              ]}
              style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              bodyStyle={{ padding: '12px', overflowY: 'auto', maxHeight: '180px' }}
              extra={paper.project_id ? (
                <Tag 
                  color="blue" 
                  onClick={() => setProjectFilter(paper.project_id || null)}
                  style={{ cursor: 'pointer' }}
                >
                  {projects.find(p => p.id === paper.project_id)?.name || 
                   `${getTranslation('项目', 'Project')} #${paper.project_id}`}
                </Tag>
              ) : null}
            >
              <div className="library-card-content">
                <p><strong>{getTranslation('作者:', 'Authors:')}</strong> {paper.authors}</p>
                {paper.journal && <p><strong>{getTranslation('期刊:', 'Journal:')}</strong> {paper.journal}</p>}
                {paper.year && <p><strong>{getTranslation('年份:', 'Year:')}</strong> {paper.year}</p>}
                {paper.doi && (
                  <p>
                    <strong>DOI:</strong> 
                    <span style={{ marginRight: 8 }}>{paper.doi}</span>
                    <Tooltip title={getTranslation('复制DOI', 'Copy DOI')}>
                      <CopyOutlined onClick={() => handleCopyDoi(paper.doi || '')} style={{ cursor: 'pointer' }} />
                    </Tooltip>
                  </p>
                )}
                {paper.project_id && (
                  <p>
                    <strong>{getTranslation('项目:', 'Project:')}</strong> 
                    <span
                      style={{ color: '#1890ff', cursor: 'pointer' }}
                      onClick={() => setProjectFilter(paper.project_id || null)}
                    >
                      {projects.find(p => p.id === paper.project_id)?.name || 
                       `${getTranslation('项目', 'Project')} #${paper.project_id}`}
                    </span>
                  </p>
                )}
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  // 添加新项目按钮点击处理
  const handleAddProjectClick = () => {
    setIsProjectModalVisible(true);
  };

  return (
    <div className="library-container">
      {contextHolder}
      <div className="library-header">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
          <Title level={3}>{getTranslation('我的文献库', 'My Library')}</Title>
        </div>
        <div style={{ maxWidth: '1200px', margin: '0 auto', marginBottom: 20 }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'flex-end',
            padding: '12px 16px'
          }}>
            <Space size="middle">
              <Input.Search
                placeholder={getTranslation('搜索文献', 'Search papers')}
                allowClear
                onSearch={value => setSearchText(value)}
                onChange={e => setSearchText(e.target.value)}
                style={{ width: 300 }}
                className="search-input"
              />
              <Select
                placeholder={getTranslation('按项目筛选', 'Filter by project')}
                style={{ width: 180 }}
                onChange={(value) => setProjectFilter(value === 'all' ? null : Number(value))}
                value={projectFilter === null ? 'all' : String(projectFilter)}
                allowClear
                onClear={() => setProjectFilter(null)}
                dropdownRender={(menu) => (
                  <>
                    {menu}
                    {projectFilter !== null && (
                      <div style={{ padding: '8px', textAlign: 'center' }}>
                        <Button 
                          type="link" 
                          onClick={() => setProjectFilter(null)} 
                          style={{ width: '100%' }}
                        >
                          {getTranslation('清除过滤', 'Clear Filter')}
                        </Button>
                      </div>
                    )}
                  </>
                )}
              >
                <Select.Option value="all">{getTranslation('所有项目', 'All Projects')}</Select.Option>
                {projects.map(project => (
                  <Select.Option key={project.id} value={String(project.id)}>
                    {project.name || project.title || `${getTranslation('项目', 'Project')} #${project.id}`}
                  </Select.Option>
                ))}
              </Select>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={() => setIsModalVisible(true)}
              >
                {getTranslation('添加论文', 'Add Paper')}
              </Button>
              <Radio.Group 
                value={displayMode}
                onChange={e => setDisplayMode(e.target.value)}
                buttonStyle="solid"
                className="display-mode-toggle"
              >
                <Radio.Button value="list"><UnorderedListOutlined /> {getTranslation('列表', 'List')}</Radio.Button>
                <Radio.Button value="card"><AppstoreOutlined /> {getTranslation('卡片', 'Cards')}</Radio.Button>
              </Radio.Group>
            </Space>
          </div>
        </div>
      </div>

      <div className="library-content">
        <div style={{ padding: '0 16px' }}>
          {displayMode === 'list' ? renderTableMode() : renderCardMode()}
        </div>
      </div>

      {/* 添加论文对话框 */}
      <Modal
        title={getTranslation('添加论文', 'Add Paper')}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleAddPaper}>
          <Form.Item
            name="title"
            label={getTranslation('标题', 'Title')}
            rules={[{ required: true, message: getTranslation('请输入论文标题', 'Please input the paper title') }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="authors"
            label={getTranslation('作者', 'Authors')}
            rules={[{ required: true, message: getTranslation('请输入作者', 'Please input the authors') }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="journal"
            label={getTranslation('期刊', 'Journal')}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="year"
            label={getTranslation('年份', 'Year')}
          >
            <Input type="number" />
          </Form.Item>
          <Form.Item
            name="doi"
            label="DOI"
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="project_id"
            label={getTranslation('所属项目', 'Project')}
          >
            <Select
              placeholder={getTranslation('选择项目', 'Select project')}
              style={{ width: '100%' }}
              dropdownRender={(menu) => (
                <>
                  {menu}
                  <Divider style={{ margin: '8px 0' }} />
                  <Button 
                    type="text" 
                    icon={<PlusOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                    onClick={handleAddProjectClick}
                  >
                    {getTranslation('创建新项目', 'Create New Project')}
                  </Button>
                </>
              )}
            >
              <Select.Option value="null">{getTranslation('无', 'None')}</Select.Option>
              {projects && projects.length > 0 ? (
                projects.map(project => (
                  <Select.Option key={project.id} value={String(project.id)}>
                    {project.name || project.title || `${getTranslation('项目', 'Project')} #${project.id}`}
                  </Select.Option>
                ))
              ) : (
                <Select.Option value="" disabled>
                  {getTranslation('暂无项目', 'No projects available')}
                </Select.Option>
              )}
            </Select>
          </Form.Item>
          <Form.Item
            name="abstract"
            label={getTranslation('摘要', 'Abstract')}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              {getTranslation('提交', 'Submit')}
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看/编辑论文对话框 */}
      <Modal
        title={getTranslation('论文详情', 'Paper Details')}
        open={editVisible}
        onCancel={() => setEditVisible(false)}
        footer={
          currentPaper ? 
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              {currentPaper.doi && (
                <Button 
                  icon={<CopyOutlined />} 
                  onClick={() => handleCopyDoi(currentPaper.doi || '')}
                >
                  {getTranslation('复制DOI', 'Copy DOI')}
                </Button>
              )}
            </div>
            <div>
              <Button onClick={() => setEditVisible(false)}>
                {getTranslation('关闭', 'Close')}
              </Button>
              <Button 
                type="primary" 
                icon={<EditOutlined />}
                onClick={() => handleEdit(currentPaper)}
                style={{ marginLeft: 8 }}
              >
                {getTranslation('编辑', 'Edit')}
              </Button>
            </div>
          </div> : null
        }
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="title"
            label={getTranslation('标题', 'Title')}
          >
            <Input disabled />
          </Form.Item>
          <Form.Item
            name="authors"
            label={getTranslation('作者', 'Authors')}
          >
            <Input disabled />
          </Form.Item>
          <Form.Item
            name="journal"
            label={getTranslation('期刊', 'Journal')}
          >
            <Input disabled />
          </Form.Item>
          <Form.Item
            name="year"
            label={getTranslation('年份', 'Year')}
          >
            <Input disabled />
          </Form.Item>
          <Form.Item
            name="doi"
            label="DOI"
          >
            <Input disabled />
          </Form.Item>
          <Form.Item
            name="project_id"
            label={getTranslation('所属项目', 'Project')}
          >
            <Select
              placeholder={getTranslation('选择项目', 'Select project')}
              style={{ width: '100%' }}
              disabled
            >
              <Select.Option value="null">{getTranslation('无', 'None')}</Select.Option>
              {projects && projects.length > 0 ? (
                projects.map(project => (
                  <Select.Option key={project.id} value={String(project.id)}>
                    {project.name || project.title || `${getTranslation('项目', 'Project')} #${project.id}`}
                  </Select.Option>
                ))
              ) : (
                <Select.Option value="" disabled>
                  {getTranslation('暂无项目', 'No projects available')}
                </Select.Option>
              )}
            </Select>
          </Form.Item>
          <Form.Item
            name="abstract"
            label={getTranslation('摘要', 'Abstract')}
          >
            <Input.TextArea rows={4} disabled />
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑论文对话框 */}
      <Modal
        title={getTranslation('编辑论文', 'Edit Paper')}
        open={editFormVisible}
        onCancel={() => setEditFormVisible(false)}
        footer={null}
      >
        <Form form={editForm} layout="vertical" onFinish={handleEditSubmit}>
          <Form.Item
            name="title"
            label={getTranslation('标题', 'Title')}
            rules={[{ required: true, message: getTranslation('请输入论文标题', 'Please input the paper title') }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="authors"
            label={getTranslation('作者', 'Authors')}
            rules={[{ required: true, message: getTranslation('请输入作者', 'Please input the authors') }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="journal"
            label={getTranslation('期刊', 'Journal')}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="year"
            label={getTranslation('年份', 'Year')}
          >
            <Input type="number" />
          </Form.Item>
          <Form.Item
            name="doi"
            label="DOI"
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="project_id"
            label={getTranslation('所属项目', 'Project')}
          >
            <Select
              placeholder={getTranslation('选择项目', 'Select project')}
              style={{ width: '100%' }}
              dropdownRender={(menu) => (
                <>
                  {menu}
                  <Divider style={{ margin: '8px 0' }} />
                  <Button 
                    type="text" 
                    icon={<PlusOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                    onClick={handleAddProjectClick}
                  >
                    {getTranslation('创建新项目', 'Create New Project')}
                  </Button>
                </>
              )}
            >
              <Select.Option value="null">{getTranslation('无', 'None')}</Select.Option>
              {projects && projects.length > 0 ? (
                projects.map(project => (
                  <Select.Option key={project.id} value={String(project.id)}>
                    {project.name || project.title || `${getTranslation('项目', 'Project')} #${project.id}`}
                  </Select.Option>
                ))
              ) : (
                <Select.Option value="" disabled>
                  {getTranslation('暂无项目', 'No projects available')}
                </Select.Option>
              )}
            </Select>
          </Form.Item>
          <Form.Item
            name="abstract"
            label={getTranslation('摘要', 'Abstract')}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              {getTranslation('保存', 'Save')}
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 创建项目对话框 */}
      <Modal
        title={getTranslation('创建新项目', 'Create New Project')}
        open={isProjectModalVisible}
        onCancel={() => setIsProjectModalVisible(false)}
        footer={null}
      >
        <Form 
          form={projectForm} 
          layout="vertical" 
          onFinish={handleCreateProject}
        >
          <Form.Item
            name="name"
            label={getTranslation('项目名称', 'Project Name')}
            rules={[{ required: true, message: getTranslation('请输入项目名称', 'Please input project name') }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label={getTranslation('项目描述', 'Project Description')}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              {getTranslation('创建', 'Create')}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Library; 
