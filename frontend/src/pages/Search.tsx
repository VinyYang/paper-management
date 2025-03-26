import React, { useState } from 'react';
import { Input, Card, Button, List, Space, Tag, Empty } from 'antd';
import { SearchOutlined, FileTextOutlined } from '@ant-design/icons';
import { paperApi } from '../services/api';

interface SearchResult {
  id: number;
  title: string;
  authors: string;
  abstract: string;
  doi: string;
  journal?: string;
  year?: number;
}

const Search: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchText.trim()) return;
    
    setLoading(true);
    try {
      const response = await paperApi.searchPapers(searchText);
      let searchResults = [];
      if (response.data) {
        if (Array.isArray(response.data)) {
          searchResults = response.data;
        } else if (response.data.results && Array.isArray(response.data.results)) {
          searchResults = response.data.results;
        } else if (typeof response.data === 'object') {
          searchResults = [response.data];
        }
      }
      setResults(searchResults);
      setSearched(true);
    } catch (error) {
      console.error('搜索失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '20px' }}>
        <Input.Search
          placeholder="输入关键词、标题或作者搜索文献"
          enterButton={<Button icon={<SearchOutlined />}>搜索</Button>}
          size="large"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onSearch={handleSearch}
          loading={loading}
        />
      </Card>

      {searched && (
        <List
          loading={loading}
          dataSource={results}
          renderItem={(item) => (
            <List.Item>
              <Card 
                title={item.title}
                style={{ width: '100%' }}
                extra={
                  <Button 
                    type="primary" 
                    icon={<FileTextOutlined />}
                    href={`/papers/${item.id}`}
                  >
                    查看详情
                  </Button>
                }
              >
                <p><strong>作者:</strong> {item.authors}</p>
                {item.journal && <p><strong>期刊:</strong> {item.journal}</p>}
                {item.year && <p><strong>年份:</strong> {item.year}</p>}
                {item.doi && (
                  <p>
                    <strong>DOI:</strong> 
                    <a href={`https://doi.org/${item.doi}`} target="_blank" rel="noopener noreferrer">
                      {item.doi}
                    </a>
                  </p>
                )}
                <p><strong>摘要:</strong> {item.abstract}</p>
                <Space wrap>
                  {item.journal && <Tag color="blue">{item.journal}</Tag>}
                  {item.year && <Tag color="green">{item.year}</Tag>}
                </Space>
              </Card>
            </List.Item>
          )}
          locale={{
            emptyText: results.length === 0 && searched ? (
              <Empty description="没有找到相关文献" />
            ) : (
              <Empty description="请输入关键词搜索" />
            )
          }}
        />
      )}
    </div>
  );
};

export default Search as React.ComponentType; 