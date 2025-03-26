import React from 'react';
import { Input, Select, Space, Radio, Tooltip, Button, theme } from 'antd';
import { SearchOutlined, AppstoreOutlined, UnorderedListOutlined, ReloadOutlined } from '@ant-design/icons';

const { Option } = Select;

interface SearchAndFilterProps {
  searchText: string;
  onSearchChange: (value: string) => void;
  viewMode: 'card' | 'list';
  onViewModeChange: (mode: 'card' | 'list') => void;
  sortField: string;
  onSortFieldChange: (field: string) => void;
  sortOrder: 'ascend' | 'descend';
  onSortOrderChange: (order: 'ascend' | 'descend') => void;
  onRefresh: () => void;
  getTranslation: (zhText: string, enText: string) => string;
  loading?: boolean;
}

const SearchAndFilter: React.FC<SearchAndFilterProps> = ({
  searchText,
  onSearchChange,
  viewMode,
  onViewModeChange,
  sortField,
  onSortFieldChange,
  sortOrder,
  onSortOrderChange,
  onRefresh,
  getTranslation,
  loading
}) => {
  const { token } = theme.useToken();
  
  return (
    <div 
      style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        marginBottom: 16, 
        flexWrap: 'wrap', 
        gap: '12px',
        padding: '16px',
        borderRadius: token.borderRadiusLG,
        backgroundColor: token.colorBgContainer,
        boxShadow: token.boxShadowTertiary,
        border: `1px solid ${token.colorBorderSecondary}`
      }}
    >
      <Space size="small" style={{ flexGrow: 1, maxWidth: '60%' }}>
        <Input
          placeholder={getTranslation('搜索论文标题、作者、摘要...', 'Search for paper title, author, abstract...')}
          value={searchText}
          onChange={(e) => onSearchChange(e.target.value)}
          prefix={<SearchOutlined />}
          allowClear
          style={{ 
            minWidth: 250,
            backgroundColor: token.colorBgContainer 
          }}
        />
        
        <Select 
          value={sortField} 
          onChange={onSortFieldChange}
          style={{ width: 140 }}
          dropdownStyle={{ backgroundColor: token.colorBgElevated }}
        >
          <Option value="created_at">{getTranslation('添加时间', 'Add Date')}</Option>
          <Option value="title">{getTranslation('标题', 'Title')}</Option>
          <Option value="authors">{getTranslation('作者', 'Authors')}</Option>
          <Option value="year">{getTranslation('年份', 'Year')}</Option>
        </Select>
        
        <Select 
          value={sortOrder} 
          onChange={onSortOrderChange}
          style={{ width: 120 }}
          dropdownStyle={{ backgroundColor: token.colorBgElevated }}
        >
          <Option value="ascend">{getTranslation('升序', 'Ascending')}</Option>
          <Option value="descend">{getTranslation('降序', 'Descending')}</Option>
        </Select>
      </Space>
      
      <Space>
        <Tooltip title={getTranslation('刷新', 'Refresh')}>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={onRefresh}
            loading={loading}
          />
        </Tooltip>
        
        <Radio.Group 
          value={viewMode} 
          onChange={(e) => onViewModeChange(e.target.value)}
          buttonStyle="solid"
        >
          <Tooltip title={getTranslation('卡片视图', 'Card View')}>
            <Radio.Button value="card"><AppstoreOutlined /></Radio.Button>
          </Tooltip>
          <Tooltip title={getTranslation('列表视图', 'List View')}>
            <Radio.Button value="list"><UnorderedListOutlined /></Radio.Button>
          </Tooltip>
        </Radio.Group>
      </Space>
    </div>
  );
};

export default SearchAndFilter; 