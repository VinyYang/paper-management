import React, { useState } from 'react';
import { Typography, Button, List, Input, Space, Modal, Form, Divider, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, FolderOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface Project {
  id: number;
  name: string;
  description?: string;
}

interface ProjectManagementProps {
  projects: Project[];
  loading: boolean;
  selectedProjectId: number | null;
  onSelectProject: (projectId: number | null) => void;
  onCreateProject: (name: string, description?: string) => void;
  onUpdateProject: (id: number, name: string) => void;
  onDeleteProject: (id: number) => void;
  getTranslation: (zhText: string, enText: string) => string;
}

const ProjectManagement: React.FC<ProjectManagementProps> = ({
  projects,
  loading,
  selectedProjectId,
  onSelectProject,
  onCreateProject,
  onUpdateProject,
  onDeleteProject,
  getTranslation
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [form] = Form.useForm();

  const showCreateModal = () => {
    setEditingProject(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const showEditModal = (project: Project) => {
    setEditingProject(project);
    form.setFieldsValue({
      name: project.name,
      description: project.description
    });
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleSubmit = () => {
    form.validateFields().then(values => {
      const { name, description } = values;
      if (editingProject) {
        onUpdateProject(editingProject.id, name);
      } else {
        onCreateProject(name, description);
      }
      setIsModalVisible(false);
      form.resetFields();
    });
  };

  const confirmDelete = (project: Project) => {
    Modal.confirm({
      title: getTranslation('确认删除', 'Confirm Deletion'),
      content: getTranslation(
        `确定要删除项目"${project.name}"吗？此操作不可撤销，但不会删除其中的论文。`,
        `Are you sure you want to delete the project "${project.name}"? This action cannot be undone, but the papers inside will not be deleted.`
      ),
      okText: getTranslation('删除', 'Delete'),
      cancelText: getTranslation('取消', 'Cancel'),
      okButtonProps: { danger: true },
      onOk: () => {
        if (selectedProjectId === project.id) {
          onSelectProject(null);
        }
        onDeleteProject(project.id);
      }
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          {getTranslation('项目管理', 'Projects')}
        </Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={showCreateModal}
          size="small"
        >
          {getTranslation('新建', 'New')}
        </Button>
      </div>
      
      <List
        loading={loading}
        dataSource={projects}
        renderItem={project => (
          <List.Item
            key={project.id}
            style={{ 
              cursor: 'pointer', 
              padding: '8px 12px',
              backgroundColor: selectedProjectId === project.id ? '#e6f7ff' : 'transparent',
              borderRadius: '4px',
              marginBottom: '4px'
            }}
            onClick={() => onSelectProject(selectedProjectId === project.id ? null : project.id)}
            actions={[
              <Tooltip title={getTranslation('编辑', 'Edit')} key="edit">
                <Button 
                  type="text" 
                  icon={<EditOutlined />} 
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    showEditModal(project);
                  }}
                />
              </Tooltip>,
              <Tooltip title={getTranslation('删除', 'Delete')} key="delete">
                <Button 
                  type="text" 
                  danger 
                  icon={<DeleteOutlined />} 
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    confirmDelete(project);
                  }}
                />
              </Tooltip>
            ]}
          >
            <List.Item.Meta
              avatar={<FolderOutlined style={{ fontSize: '18px', color: '#1890ff' }} />}
              title={project.name}
              description={project.description}
            />
          </List.Item>
        )}
        locale={{ emptyText: getTranslation('暂无项目', 'No projects yet') }}
      />

      <Divider />
      
      <div style={{ marginTop: 8 }}>
        <Button 
          type="text" 
          style={{ width: '100%', textAlign: 'left' }}
          onClick={() => onSelectProject(null)}
        >
          {getTranslation('所有论文', 'All Papers')}
        </Button>
      </div>
      
      <Modal
        title={
          editingProject 
            ? getTranslation('编辑项目', 'Edit Project')
            : getTranslation('创建新项目', 'Create New Project')
        }
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={handleCancel}
        okText={getTranslation('保存', 'Save')}
        cancelText={getTranslation('取消', 'Cancel')}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label={getTranslation('项目名称', 'Project Name')}
            rules={[{ required: true, message: getTranslation('请输入项目名称', 'Please enter project name') }]}
          >
            <Input placeholder={getTranslation('输入项目名称', 'Enter project name')} />
          </Form.Item>
          
          <Form.Item
            name="description"
            label={getTranslation('项目描述', 'Project Description')}
          >
            <Input.TextArea 
              placeholder={getTranslation('输入项目描述（可选）', 'Enter project description (optional)')} 
              rows={3}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectManagement; 