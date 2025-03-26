import React from 'react';
import { Button, Tooltip } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

interface DoiDetectorProps {
  text: string;
}

const DoiDetector: React.FC<DoiDetectorProps> = ({ text }) => {
  // DOI 格式的正则表达式匹配
  const doiRegex = /\b(10\.\d{4,}(?:\.\d+)*\/(?:(?!["&'<>])\S)+)\b/g;
  let matches = [];
  let match;
  let lastIndex = 0;
  const result = [];

  // 查找文本中的所有 DOI
  while ((match = doiRegex.exec(text)) !== null) {
    const doi = match[0];
    const index = match.index;
    
    // 添加 DOI 之前的文本
    if (index > lastIndex) {
      result.push(<span key={`text-${lastIndex}`}>{text.substring(lastIndex, index)}</span>);
    }
    
    // 添加带有查找按钮的 DOI
    result.push(
      <span key={`doi-${index}`} style={{ position: 'relative', backgroundColor: '#f0f9ff', padding: '0 4px', borderRadius: '2px' }}>
        {doi}
        <Tooltip title="在 Sci-Hub 查找">
          <Button 
            size="small" 
            type="text" 
            icon={<SearchOutlined />} 
            onClick={() => window.open(`https://sci-hubtw.hkvisa.net/${doi}`, '_blank')}
            style={{ 
              position: 'absolute', 
              top: '-10px', 
              right: '-10px',
              backgroundColor: '#1890ff',
              color: 'white',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 0,
              fontSize: '12px'
            }}
          />
        </Tooltip>
      </span>
    );
    
    lastIndex = index + doi.length;
  }
  
  // 添加剩余文本
  if (lastIndex < text.length) {
    result.push(<span key={`text-${lastIndex}`}>{text.substring(lastIndex)}</span>);
  }
  
  return <>{result}</>;
};

export default DoiDetector; 