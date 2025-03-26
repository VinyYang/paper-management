import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Tabs, Button, message, Rate, Table, Spin, Typography, Tooltip, Upload, Space, Popconfirm } from 'antd';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import PDFViewer from '../components/PDFViewer';
import { publicationRankApi, paperApi, errorManager } from '../services/api';
import { UploadOutlined, DownloadOutlined, FilePdfOutlined, DeleteOutlined, CopyOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { RcFile } from 'antd/es/upload';
import { RankResult } from '../services/api/publicationRankApi';
import { useSettings } from '../contexts/SettingsContext';

const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;

interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract: string;
  doi: string;
  file_path: string;
  year: number;
  journal: string;
  citations: number;
  has_pdf: boolean;
  local_pdf_path?: string;
}

interface Note {
  id: number;
  content: string;
  page_number: number;
  created_at: string;
  updated_at: string;
}

// 使用RankResult[]替代旧的PublicationRank类型
// 保留旧的PublicationRank接口定义作为参考
interface OldPublicationRank {
  customRank?: {
    rankInfo: Array<{
      uuid: string;
      abbName: string;
      oneRankText: string;
      twoRankText: string;
      threeRankText?: string;
      fourRankText?: string;
      fiveRankText?: string;
    }>;
    rank: string[];
  };
  officialRank?: {
    all: Record<string, string>;
    select: Record<string, string>;
  };
}

// 期刊等级样式配置
const rankStyleConfig = {
  // 等级颜色配置
  colors: {
    level1: '#ff9999',
    level2: '#86dad1',
    level3: '#ffe78f',
    level4: '#ffd4a9',
    level5: '#cce5ff'
  },
  // 字体配置
  font: {
    color: '#000000',
    bold: true,
    size: '13px'
  },
  // 其他配置
  showDetailTips: true,
  showScihub: true,
  scihubLinks: [
    'https://sci-hub.se/',  // 官方主站，经实时检测可用
    'https://sci-hub.st/',  // 官方最新检测可用
    'https://sci-hub.ru/',  // 官方长期稳定
    'https://sci-hub.ee/',  // 推荐镜像站，多平台推荐
    'https://sci-hub.cat/'  // 推荐镜像站，欧洲节点访问较快
  ]
};

// 根据等级获取对应的样式
const getRankStyle = (rankLevel: number) => {
  let bgColor = '';
  
  switch(rankLevel) {
    case 1: bgColor = rankStyleConfig.colors.level1; break;
    case 2: bgColor = rankStyleConfig.colors.level2; break;
    case 3: bgColor = rankStyleConfig.colors.level3; break;
    case 4: bgColor = rankStyleConfig.colors.level4; break;
    case 5: bgColor = rankStyleConfig.colors.level5; break;
    default: bgColor = '#ffffff';
  }
  
  return {
    backgroundColor: bgColor,
    color: rankStyleConfig.font.color,
    fontWeight: rankStyleConfig.font.bold ? 'bold' : 'normal',
    fontSize: rankStyleConfig.font.size,
    padding: '2px 6px',
    borderRadius: '4px',
    display: 'inline-block',
    margin: '2px'
  };
};

// 获取等级级别（用于自定义等级）
const getRankLevel = (rankStr: string): number => {
  const parts = rankStr.split('&&&');
  if (parts.length !== 2) return 0;
  return parseInt(parts[1]);
};

const PaperDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const parsedId = parseInt(id || '0');
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('info');
  const [notes, setNotes] = useState<Note[]>([]);
  // 修改journalRank的类型为RankResult[]
  const [journalRank, setJournalRank] = useState<RankResult[] | null>(null);
  const [rankLoading, setRankLoading] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();
  const { language } = useSettings();

  // 添加翻译函数
  const getTranslation = (zhText: string, enText: string) => {
    return language === 'zh_CN' ? zhText : enText;
  };

  useEffect(() => {
    if (parsedId) {
      fetchPaperDetails();
      fetchNotes();
    }
  }, [parsedId]);

  useEffect(() => {
    // 当获取到论文信息且有期刊名称时，获取期刊等级信息
    if (paper && paper.journal) {
      fetchJournalRank(paper.journal);
    }
  }, [paper]);

  const fetchPaperDetails = async () => {
    try {
      setLoading(true);
      const response = await paperApi.getPaper(parsedId);
      setPaper(response.data);
    } catch (error) {
      messageApi.error('获取文献详情失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchJournalRank = async (journalName: string) => {
    if (!journalName) return;
    
    try {
      setRankLoading(true);
      
      // 首先尝试从localStorage中获取缓存的期刊等级信息
      const cachedRankInfo = localStorage.getItem(`journal_rank_${journalName}`);
      if (cachedRankInfo) {
        try {
          const parsedRankInfo = JSON.parse(cachedRankInfo) as RankResult[];
          if (parsedRankInfo && parsedRankInfo.length > 0) {
            setJournalRank(parsedRankInfo);
            setRankLoading(false);
            console.log('从缓存中获取期刊等级信息成功:', journalName);
            return;
          }
        } catch (e) {
          console.error('解析缓存的期刊等级信息失败:', e);
        }
      }
      
      // 如果没有缓存或解析失败，则从API获取
      console.log('从API获取期刊等级信息:', journalName);
      const response = await publicationRankApi.getPublicationRank(journalName);
      if (response && response.length > 0) {
        setJournalRank(response);
        
        // 缓存获取的期刊等级信息
        try {
          localStorage.setItem(`journal_rank_${journalName}`, JSON.stringify(response));
        } catch (e) {
          console.error('缓存期刊等级信息失败:', e);
        }
      } else {
        setJournalRank(null);
        console.error('获取期刊等级信息失败，未找到相关数据');
      }
    } catch (error) {
      console.error('获取期刊等级信息出错:', error);
      setJournalRank(null);
    } finally {
      setRankLoading(false);
    }
  };

  const fetchNotes = async () => {
    try {
      const response = await paperApi.getPaperNotes(parsedId);
      setNotes(response.data.notes);
    } catch (error) {
      errorManager.showErrorOnce('获取笔记失败');
    }
  };

  const handleCopyDoi = () => {
    if (paper?.doi) {
      navigator.clipboard.writeText(paper.doi)
        .then(() => {
          messageApi.success('DOI已复制到剪贴板');
        })
        .catch(() => {
          messageApi.error('复制失败，请手动复制');
        });
    }
  };

  // 修改renderOfficialRanks方法适配新的RankResult[]类型
  const renderOfficialRanks = () => {
    if (!journalRank || journalRank.length === 0) return null;
    
    const officialRanks = journalRank.filter(rank => rank.type === 'official');
    
    // 如果没有官方等级信息，显示提示
    if (officialRanks.length === 0) {
      return <Text type="secondary">无官方期刊等级信息</Text>;
    }

    return (
      <div className="rank-list">
        {officialRanks.map((rank, index) => {
          // 根据新的分级体系确定等级级别
          let rankLevel = 3; // 默认为中等级别
          if (rank.rank.includes('CCF-A')) rankLevel = 1;
          else if (rank.rank.includes('CCF-B')) rankLevel = 2; 
          else if (rank.rank.includes('CCF-C')) rankLevel = 3;
          else if (rank.rank.includes('CSSCI')) rankLevel = 2;
          else if (rank.rank.includes('SCI')) rankLevel = 1;
          else if (rank.rank.includes('EI')) rankLevel = 2;
          else if (rank.rank.includes('预印本') || rank.rank.includes('聚合平台') || rank.rank.includes('数据库')) rankLevel = 3;
          
          return (
            <div key={index} className="rank-item" style={{ marginBottom: '8px' }}>
              <span style={{ marginRight: '10px' }}>{rank.source}:</span>
              <span style={getRankStyle(rankLevel)}>{rank.rank}</span>
              
              {rankStyleConfig.showDetailTips && (
                <Tooltip title={`${rank.source}分类: ${rank.rank}`}>
                  <Button type="link" size="small" style={{ padding: '0 4px' }}>?</Button>
                </Tooltip>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  // 修改renderCustomRanks方法适配新的RankResult[]类型
  const renderCustomRanks = () => {
    if (!journalRank || journalRank.length === 0) return null;
    
    const customRanks = journalRank.filter(rank => rank.type === 'custom');
    
    // 如果没有自定义等级信息，显示提示
    if (customRanks.length === 0) {
      return <Text type="secondary">无自定义期刊等级信息</Text>;
    }
    
    return (
      <div className="rank-list">
        {customRanks.map((rank, index) => (
          <div key={index} className="rank-item" style={{ marginBottom: '8px' }}>
            <span style={{ marginRight: '10px' }}>{rank.source}:</span>
            <span style={getRankStyle(rank.level || 3)}>{rank.rank}</span>
            
            {rankStyleConfig.showDetailTips && (
              <Tooltip title={`${rank.source} 数据集将此期刊评为 ${rank.rank} 级别`}>
                <Button type="link" size="small" style={{ padding: '0 4px' }}>?</Button>
              </Tooltip>
            )}
          </div>
        ))}
      </div>
    );
  };

  // 渲染简要期刊等级标签
  const renderSimpleJournalRank = () => {
    if (!journalRank || journalRank.length === 0) return null;
    
    // 只展示前2个最重要的等级
    const topRanks = journalRank
      .sort((a, b) => {
        // 优先显示官方等级和高等级
        if (a.type === 'official' && b.type !== 'official') return -1;
        if (a.type !== 'official' && b.type === 'official') return 1;
        
        // 如果都是官方或都是自定义，按等级排序
        const aLevel = a.type === 'official' ? 
          (a.rank.includes('CCF-A') || a.rank.includes('SCI') ? 1 : 
           a.rank.includes('CCF-B') || a.rank.includes('EI') || a.rank.includes('CSSCI') ? 2 : 3) : 
          (a.level || 3);
        
        const bLevel = b.type === 'official' ? 
          (b.rank.includes('CCF-A') || b.rank.includes('SCI') ? 1 : 
           b.rank.includes('CCF-B') || b.rank.includes('EI') || b.rank.includes('CSSCI') ? 2 : 3) : 
          (b.level || 3);
        
        return aLevel - bLevel;
      })
      .slice(0, 2);
    
    return (
      <div style={{ display: 'inline-flex', marginLeft: 8, gap: '4px' }}>
        {topRanks.map((rank, index) => {
          // 确定等级样式
          let rankLevel = rank.level || 3;
          if (rank.type === 'official') {
            if (rank.rank.includes('CCF-A') || rank.rank.includes('SCI')) rankLevel = 1;
            else if (rank.rank.includes('CCF-B') || rank.rank.includes('EI') || rank.rank.includes('CSSCI')) rankLevel = 2;
            else rankLevel = 3;
          }
          
          return (
            <Tooltip key={index} title={`${rank.source}: ${rank.rank}`}>
              <span style={getRankStyle(rankLevel)}>{rank.rank}</span>
            </Tooltip>
          );
        })}
        {journalRank.length > 2 && (
          <Tooltip title={getTranslation('点击"期刊排名"选项卡查看更多', 'Click "Journal Ranking" tab to see more')}>
            <Button type="link" size="small" style={{ padding: '0 4px', minWidth: 'auto' }}>+{journalRank.length - 2}</Button>
          </Tooltip>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载中...</div>
      </div>
    );
  }

  if (!paper) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>论文未找到</Title>
        <div>无法找到该论文，它可能已被删除或您没有访问权限。</div>
      </div>
    );
  }

  return (
    <div className="paper-detail-container">
      {contextHolder}
      {/* 主要信息卡片 */}
      <Card className="paper-main-card">
        <Title level={3}>{paper.title}</Title>
        <div className="paper-meta">
          <div><strong>作者:</strong> {paper.authors}</div>
          {paper.journal && (
            <div>
              <strong>期刊:</strong> {paper.journal}
              {renderSimpleJournalRank()}
            </div>
          )}
          {paper.year && <div><strong>年份:</strong> {paper.year}</div>}
          {paper.doi && (
            <div>
              <strong>DOI:</strong> {paper.doi}
              <Tooltip title="复制DOI">
                <Button 
                  type="text" 
                  icon={<CopyOutlined />} 
                  onClick={handleCopyDoi}
                  style={{ marginLeft: 8 }}
                />
              </Tooltip>
            </div>
          )}
          {paper.citations !== undefined && (
            <div><strong>引用次数:</strong> {paper.citations}</div>
          )}
        </div>
        
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="摘要信息" key="info">
            <div className="paper-abstract">
              <div>
                <strong>摘要:</strong>
                <Paragraph>{paper.abstract}</Paragraph>
              </div>
            </div>
          </TabPane>
          
          <TabPane tab="笔记" key="notes">
            <Table 
              dataSource={notes} 
              columns={[
                { title: '页码', dataIndex: 'page_number', key: 'page' },
                { title: '内容', dataIndex: 'content', key: 'content' },
                { title: '创建时间', dataIndex: 'created_at', key: 'created_at' }
              ]} 
              rowKey="id"
            />
          </TabPane>
          
          <TabPane tab="期刊排名" key="rank">
            <Card>
              <Spin spinning={rankLoading}>
                {renderOfficialRanks()}
                {renderCustomRanks()}
              </Spin>
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default PaperDetail; 