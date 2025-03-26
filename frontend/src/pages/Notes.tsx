import React, { useState, useEffect } from 'react';
import { 
  Card, Typography, Modal, Form, Input, Select, message, Button, List 
} from 'antd';
import { 
  TagOutlined
} from '@ant-design/icons';
import { noteApi, paperApi } from '../services/api';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface Note {
  id: number;
  content: string;
  paper_id: number;
  user_id: number;
  page_number?: number;
  created_at: string;
  updated_at: string;
  paper_title: string;
  concepts: { id: number; name: string }[];
  title?: string;
}

interface Paper {
  id: number;
  title: string;
}

const Notes: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [createVisible, setCreateVisible] = useState(false);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [form] = Form.useForm();
  const [createForm] = Form.useForm();
  const navigate = useNavigate();

  // 获取笔记列表
  const fetchNotes = async () => {
    setIsLoading(true);
    try {
      const response = await noteApi.getNotes();
      // 确保 notes 是数组类型
      if (response.data && response.data.notes && Array.isArray(response.data.notes)) {
        setNotes(response.data.notes);
      } else {
        console.warn('笔记数据格式不正确:', response.data);
        setNotes([]);
      }
    } catch (error) {
      message.error('获取笔记列表失败');
      console.error(error);
      setNotes([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 获取文献列表
  const fetchPapers = async () => {
    try {
      const response = await paperApi.getPapers();
      if (response.data && Array.isArray(response.data)) {
        setPapers(response.data);
      } else {
        console.warn('文献数据格式不正确:', response.data);
        setPapers([]);
      }
    } catch (error) {
      console.error('获取文献列表失败', error);
      setPapers([]);
    }
  };

  useEffect(() => {
    fetchNotes();
    fetchPapers();
  }, []);

  // 删除笔记
  const handleDeleteNote = (id: number) => {
    Modal.confirm({
      title: '确定要删除这条笔记吗？',
      content: '删除后将无法恢复',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await noteApi.deleteNote(id);
          message.success('笔记删除成功');
          fetchNotes();
          if (selectedNote?.id === id) {
            setDetailVisible(false);
          }
        } catch (error) {
          message.error('笔记删除失败');
          console.error(error);
        }
      }
    });
  };

  // 编辑笔记
  const handleEditNote = () => {
    if (!selectedNote) return;
    
    form.setFieldsValue({
      content: selectedNote.content,
      page_number: selectedNote.page_number,
    });
    
    setEditVisible(true);
  };

  // 提交编辑
  const handleEditSubmit = async (values: any) => {
    if (!selectedNote) return;
    
    try {
      await noteApi.updateNote(selectedNote.id, {
        content: values.content,
        page_number: values.page_number,
      } as Partial<Note>);
      
      message.success('笔记更新成功');
      setEditVisible(false);
      fetchNotes();
      
      // 更新当前选中的笔记
      const updatedNote = {
        ...selectedNote,
        content: values.content,
        page_number: values.page_number,
      };
      
      setSelectedNote(updatedNote);
    } catch (error) {
      message.error('笔记更新失败');
      console.error(error);
    }
  };

  // 创建新笔记
  const handleCreateNote = async (values: any) => {
    try {
      await noteApi.createNote({
        content: values.content,
        paper_id: values.paper_id,
        page_number: values.page_number,
      } as Partial<Note>);
      
      message.success('笔记创建成功');
      setCreateVisible(false);
      createForm.resetFields();
      fetchNotes();
    } catch (error) {
      message.error('笔记创建失败');
      console.error(error);
    }
  };

  // 查看关联文献
  const handleViewPaper = (paperId: number) => {
    navigate(`/papers/${paperId}`);
  };

  // 根据搜索条件筛选笔记
  const getFilteredNotes = () => {
    if (!Array.isArray(notes)) {
      return [];
    }
    return notes.filter(note => 
      note.content.toLowerCase().includes(searchText.toLowerCase()) ||
      note.paper_title.toLowerCase().includes(searchText.toLowerCase()) ||
      (note.concepts && Array.isArray(note.concepts) && 
        note.concepts.some(concept => concept.name.toLowerCase().includes(searchText.toLowerCase())))
    );
  };

  // 显示笔记详情
  const showNoteDetail = (note: Note) => {
    setSelectedNote(note);
    setDetailVisible(true);
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={3}>笔记</Title>
        <p>在这里管理您的笔记和读书笔记。</p>
        <div style={{ marginTop: '16px' }}>
          <Button type="primary" onClick={() => setCreateVisible(true)}>
            新建笔记
          </Button>
        </div>
      </Card>

      {/* 笔记列表 */}
      <Card style={{ marginTop: '16px' }}>
        <List
          loading={isLoading}
          dataSource={getFilteredNotes()}
          renderItem={(note) => (
            <List.Item
              key={note.id}
              actions={[
                <Button 
                  key="view" 
                  type="link" 
                  onClick={() => showNoteDetail(note)}
                >
                  查看
                </Button>,
                <Button 
                  key="edit" 
                  type="link" 
                  onClick={() => {
                    setSelectedNote(note);
                    form.setFieldsValue({
                      content: note.content,
                      page_number: note.page_number,
                    });
                    setEditVisible(true);
                  }}
                >
                  编辑
                </Button>,
                <Button 
                  key="delete" 
                  type="link" 
                  danger 
                  onClick={() => handleDeleteNote(note.id)}
                >
                  删除
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={note.paper_title || '无标题'}
                description={note.content}
              />
            </List.Item>
          )}
        />
      </Card>

      {/* 创建笔记的对话框 */}
      <Modal
        title="创建新笔记"
        visible={createVisible}
        onCancel={() => setCreateVisible(false)}
        footer={null}
      >
        <Form form={createForm} onFinish={handleCreateNote} layout="vertical">
          <Form.Item 
            name="paper_id" 
            label="关联文献"
            rules={[{ required: true, message: '请选择关联文献' }]}
          >
            <Select placeholder="选择文献">
              {papers.map(paper => (
                <Option key={paper.id} value={paper.id}>{paper.title}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item 
            name="content" 
            label="笔记内容"
            rules={[{ required: true, message: '请输入笔记内容' }]}
          >
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="page_number" label="页码">
            <Input type="number" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑笔记的对话框 */}
      <Modal
        title="编辑笔记"
        visible={editVisible}
        onCancel={() => setEditVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleEditSubmit} layout="vertical">
          <Form.Item 
            name="content" 
            label="笔记内容"
            rules={[{ required: true, message: '请输入笔记内容' }]}
          >
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="page_number" label="页码">
            <Input type="number" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              保存
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 笔记详情对话框 */}
      <Modal
        title="笔记详情"
        visible={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="back" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
          <Button 
            key="edit" 
            type="primary" 
            onClick={() => {
              setDetailVisible(false);
              form.setFieldsValue({
                content: selectedNote?.content,
                page_number: selectedNote?.page_number,
              });
              setEditVisible(true);
            }}
          >
            编辑
          </Button>
        ]}
      >
        {selectedNote && (
          <div>
            <p><strong>文献:</strong> {selectedNote.paper_title}</p>
            {selectedNote.page_number && <p><strong>页码:</strong> {selectedNote.page_number}</p>}
            <p><strong>内容:</strong></p>
            <div style={{ whiteSpace: 'pre-wrap' }}>{selectedNote.content}</div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Notes as React.ComponentType; 