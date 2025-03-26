import React, { useState, useEffect } from 'react';
import { List, Card, Button, Input, Upload, Modal, message } from 'antd';
import { UploadOutlined, SearchOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const { Search } = Input;

interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract: string;
  doi: string;
  file_path: string;
}

const PaperList: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [doi, setDoi] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPapers();
  }, []);

  const fetchPapers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/papers');
      setPapers(response.data.papers);
    } catch (error) {
      message.error('获取文献列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleImportByDoi = async () => {
    try {
      setLoading(true);
      await api.post('/api/papers/import', null, {
        params: { doi }
      });
      message.success('文献导入成功');
      setImportModalVisible(false);
      setDoi('');
      fetchPapers();
    } catch (error) {
      message.error('文献导入失败');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('pdf_file', file);
      await api.post('/api/papers/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success('文献导入成功');
      fetchPapers();
    } catch (error) {
      message.error('文献导入失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<UploadOutlined />}
          onClick={() => setImportModalVisible(true)}
          style={{ marginRight: 16 }}
        >
          导入文献
        </Button>
        <Search
          placeholder="搜索文献"
          allowClear
          enterButton={<SearchOutlined />}
          style={{ width: 300 }}
        />
      </div>

      <List
        loading={loading}
        grid={{ gutter: 16, column: 3 }}
        dataSource={papers}
        renderItem={(paper) => (
          <List.Item>
            <Card
              hoverable
              title={paper.title}
              onClick={() => navigate(`/paper/${paper.id}`)}
            >
              <p><strong>作者：</strong>{paper.authors}</p>
              <p><strong>DOI：</strong>{paper.doi}</p>
              <p><strong>摘要：</strong>{paper.abstract}</p>
            </Card>
          </List.Item>
        )}
      />

      <Modal
        title="导入文献"
        open={importModalVisible}
        onOk={handleImportByDoi}
        onCancel={() => setImportModalVisible(false)}
        confirmLoading={loading}
      >
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="输入DOI"
            value={doi}
            onChange={(e) => setDoi(e.target.value)}
          />
        </div>
        <Upload
          beforeUpload={(file) => {
            handleFileUpload(file);
            return false;
          }}
          showUploadList={false}
        >
          <Button icon={<UploadOutlined />}>上传PDF文件</Button>
        </Upload>
      </Modal>
    </div>
  );
};

export default PaperList as React.ComponentType; 