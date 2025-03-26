import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const AboutPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>关于我们</Title>
        <Paragraph>
          这是一个学术文献管理系统，帮助研究人员有效地管理文献资源。
        </Paragraph>
        <Paragraph>
          系统提供文献收集、分类、笔记管理、知识图谱等功能，助力科研工作。
        </Paragraph>
      </Card>
    </div>
  );
};

export default AboutPage as React.ComponentType; 