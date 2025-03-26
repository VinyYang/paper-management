import React, { useEffect, useState } from 'react';
import { Card, Button, List, Modal, Form, Input, message, Space } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { projectApi } from '../services/api';

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const navigate = useNavigate();

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await projectApi.getProjects();
      console.log("获取项目列表响应:", response);
      if (response && response.data) {
        setProjects(response.data);
      } else if (Array.isArray(response)) {
        setProjects(response);
      } else {
        console.error("无法解析项目数据:", response);
        setProjects([]);
      }
    } catch (error) {
      console.error('获取项目列表失败', error);
      message.error('获取项目列表失败');
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (values: any) => {
    try {
      await projectApi.createProject(values);
      message.success('项目创建成功');
      setModalVisible(false);
      form.resetFields();
      fetchProjects();
    } catch (error) {
      message.error('项目创建失败');
    }
  };

  const handleUpdateProject = async (values: any) => {
    if (!editingProject) return;
    try {
      await projectApi.updateProject(editingProject.id, values);
      message.success('项目更新成功');
      setModalVisible(false);
      form.resetFields();
      setEditingProject(null);
      fetchProjects();
    } catch (error) {
      message.error('项目更新失败');
    }
  };

  const handleDeleteProject = async (id: number) => {
    try {
      await projectApi.deleteProject(id);
      message.success('项目删除成功');
      fetchProjects();
    } catch (error) {
      message.error('项目删除失败');
    }
  };

  const showModal = (project?: Project) => {
    if (project) {
      setEditingProject(project);
      form.setFieldsValue(project);
    } else {
      setEditingProject(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>我的项目</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()}>
          创建项目
        </Button>
      </div>

      <List
        loading={loading}
        grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
        dataSource={projects}
        locale={{ emptyText: '暂无研究项目，请点击"创建项目"按钮新建项目' }}
        renderItem={(project) => (
          <List.Item>
            <Card
              hoverable
              title={project.name}
              onClick={() => navigate(`/projects/${project.id}`)}
              extra={
                <Space>
                  <Button
                    type="text"
                    icon={<EditOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      showModal(project);
                    }}
                  />
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      Modal.confirm({
                        title: '确认删除',
                        content: '确定要删除这个项目吗？',
                        onOk: () => handleDeleteProject(project.id),
                      });
                    }}
                  />
                </Space>
              }
            >
              <p>{project.description}</p>
              <p>创建时间：{new Date(project.created_at).toLocaleString()}</p>
            </Card>
          </List.Item>
        )}
      />

      <Modal
        title={editingProject ? '编辑项目' : '创建项目'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setEditingProject(null);
        }}
      >
        <Form
          form={form}
          onFinish={editingProject ? handleUpdateProject : handleCreateProject}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label="项目描述"
          >
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Projects as React.ComponentType; 