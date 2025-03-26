import React, { useState, useEffect } from 'react';
import { List, Card, Button, Input, Modal, Form, message, Tag, Space, Switch } from 'antd';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface Note {
  id: number;
  title: string;
  content: string;
  paper_id: number | null;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  tags: string | null;
  paper_title?: string;
  paper_authors?: string;
}

const NoteList: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [form] = Form.useForm();
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/notes');
      setNotes(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取笔记列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingNote(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (note: Note) => {
    setEditingNote(note);
    form.setFieldsValue(note);
    setModalVisible(true);
  };

  const handleDelete = async (noteId: number) => {
    try {
      await api.delete(`/api/notes/${noteId}`);
      message.success('删除笔记成功');
      fetchNotes();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除笔记失败');
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingNote) {
        await api.put(`/api/notes/${editingNote.id}`, {
          ...values,
          paper_id: values.paper_id || null
        });
        message.success('更新笔记成功');
      } else {
        await api.post('/api/notes', {
          ...values,
          paper_id: values.paper_id || null
        });
        message.success('创建笔记成功');
      }
      setModalVisible(false);
      fetchNotes();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存笔记失败');
    }
  };

  const renderTags = (tags: string | null) => {
    if (!tags) return null;
    return tags.split(',').map((tag, index) => (
      <Tag key={index} color="blue">{tag.trim()}</Tag>
    ));
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
        >
          新建笔记
        </Button>
      </div>

      <List
        grid={{ gutter: 16, column: 3 }}
        dataSource={notes}
        loading={loading}
        renderItem={(note) => (
          <List.Item>
            <Card
              title={note.title}
              extra={
                <Space>
                  <Button
                    type="link"
                    icon={<EditOutlined />}
                    onClick={() => handleEdit(note)}
                  >
                    编辑
                  </Button>
                  <Button
                    type="link"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDelete(note.id)}
                  >
                    删除
                  </Button>
                </Space>
              }
            >
              <p>{note.content.substring(0, 100)}...</p>
              {note.paper_title && (
                <p>
                  <strong>关联文献：</strong>
                  {note.paper_title}
                </p>
              )}
              {renderTags(note.tags)}
              <p>
                <small>
                  创建时间：{new Date(note.created_at).toLocaleString()}
                </small>
              </p>
            </Card>
          </List.Item>
        )}
      />

      <Modal
        title={editingNote ? '编辑笔记' : '新建笔记'}
        open={modalVisible}
        onOk={form.submit}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
      >
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
        >
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <Input.TextArea rows={6} />
          </Form.Item>

          <Form.Item
            name="tags"
            label="标签"
            help="多个标签用逗号分隔"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="is_public"
            label="是否公开"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default NoteList as React.ComponentType; 