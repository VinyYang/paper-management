import React, { useState, useEffect } from 'react';
import { Card, Button, Tabs, Row, Col, Tag, Spin, message, Typography, Space, Empty, Divider, Modal, Select, Dropdown, Menu, Alert } from 'antd';
import { ReloadOutlined, BookOutlined, DownloadOutlined, StarOutlined, EyeOutlined, FileSearchOutlined, DownOutlined, ThunderboltOutlined, FireOutlined } from '@ant-design/icons';
import { journalApi, recommendationApi, scihubApi, errorManager } from '../services/api';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

// 确保数据是数组的帮助函数
const ensureArray = <T extends any>(data: any): T[] => {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  return [];
};

interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract: string;
  doi: string;
  url: string;
  publication_date: string;
  source?: string;
}

interface LatestPaper extends Paper {
  journal?: {
    id: number;
    name: string;
    abbreviation: string;
    category: string;
    ranking: string;
  };
}

interface Recommendation {
  id: number;
  paper_id: number;
  score: number;
  reason: string;
  paper: Paper;
}

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [randomRecommendations, setRandomRecommendations] = useState<Recommendation[]>([]);
  const [latestPapers, setLatestPapers] = useState<LatestPaper[]>([]);
  const [categories, setCategories] = useState<string[]>(['全部', '计算机', '医学', '生物学', '农学', '物理学', '化学', '经济学', '社会学', '心理学', '环境科学', '文学', '历史学', '地理学', '哲学']);
  const [randomCategory, setRandomCategory] = useState<string>('全部');
  const [loading, setLoading] = useState<boolean>(true);
  const [randomLoading, setRandomLoading] = useState<boolean>(false);
  const [refreshingRecommendations, setRefreshingRecommendations] = useState<boolean>(false);
  const [refreshingLatestPapers, setRefreshingLatestPapers] = useState<boolean>(false);
  const [viewAbstractId, setViewAbstractId] = useState<number | null>(null);

  // 获取推荐
  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const { data } = await recommendationApi.getRecommendations(10);
      console.log('获取到的推荐数据:', data);
      
      const recommendationsArray = ensureArray<Recommendation>(
        data && data.recommendations ? data.recommendations : []
      );
      setRecommendations(recommendationsArray);
    } catch (error) {
      console.error('获取推荐失败:', error);
      errorManager.showErrorOnce('获取推荐失败，请稍后重试');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  // 获取随机推荐
  const fetchRandomRecommendations = async (category?: string) => {
    try {
      setRandomLoading(true);
      // AI分类改为使用计算机分类
      let requestCategory = category;
      if (category === 'AI') {
        requestCategory = '计算机';
      }
      const { data } = await recommendationApi.getRandomRecommendations(requestCategory, 10);
      console.log('获取到的随机推荐数据:', data);
      
      const recommendationsArray = ensureArray<Recommendation>(
        data && data.recommendations ? data.recommendations : []
      );
      setRandomRecommendations(recommendationsArray);
    } catch (error) {
      console.error('获取随机推荐失败:', error);
      errorManager.showErrorOnce('获取随机推荐失败，请稍后重试');
      setRandomRecommendations([]);
    } finally {
      setRandomLoading(false);
    }
  };

  // 获取最新论文
  const fetchLatestPapers = async (category?: string) => {
    try {
      setLoading(true);
      // 始终使用计算机分类
      const { data } = await journalApi.getLatestPapers('计算机', 10);
      setLatestPapers(data || []);
    } catch (error) {
      console.error('获取最新论文失败', error);
      errorManager.showErrorOnce('获取最新论文失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 强制刷新推荐（不使用缓存）
  const forceRefreshRecommendations = async () => {
    try {
      setRefreshingRecommendations(true);
      await recommendationApi.forceRefreshRecommendations();
      errorManager.showSuccessOnce('刷新推荐任务已启动，这可能需要几分钟，请稍后刷新页面查看');
      // 延迟5秒后重新获取推荐
      setTimeout(() => {
        fetchRecommendations();
        setRefreshingRecommendations(false);
      }, 5000);
    } catch (error) {
      console.error('刷新推荐失败:', error);
      errorManager.showErrorOnce('刷新推荐失败，请稍后重试');
      setRefreshingRecommendations(false);
    }
  };

  // 强制刷新随机推荐（不使用缓存）
  const forceRefreshRandomRecommendations = async () => {
    try {
      setRandomLoading(true);
      const category = randomCategory !== '全部' ? randomCategory : undefined;
      await recommendationApi.forceRefreshRandomRecommendations(category);
      errorManager.showSuccessOnce('刷新随机推荐任务已启动，这可能需要几分钟，请稍后刷新页面查看');
      // 延迟5秒后重新获取随机推荐
      setTimeout(() => {
        fetchRandomRecommendations(category);
        setRandomLoading(false);
      }, 5000);
    } catch (error) {
      console.error('刷新随机推荐失败:', error);
      errorManager.showErrorOnce('刷新随机推荐失败，请稍后重试');
      setRandomLoading(false);
    }
  };

  // 强制刷新最新论文（不使用缓存）
  const forceRefreshLatestPapers = async () => {
    try {
      setRefreshingLatestPapers(true);
      await journalApi.forceRefreshLatestPapers();
      errorManager.showSuccessOnce('刷新任务已启动，这可能需要几分钟，请稍后刷新页面查看');
      // 延迟5秒后重新获取最新论文
      setTimeout(() => {
        fetchLatestPapers();
        setRefreshingLatestPapers(false);
      }, 5000);
    } catch (error) {
      console.error('刷新最新论文失败:', error);
      // 使用类型保护和断言来处理可能的API错误响应
      errorManager.showErrorOnce('刷新最新论文失败，请稍后重试');
      setRefreshingLatestPapers(false);
    }
  };

  // 打开Sci-Hub
  const handleOpenSciHub = async (doi: string) => {
    try {
      const result = await scihubApi.downloadPdf(doi);
      console.log('Sci-Hub下载结果:', result);
      if (result) {
        errorManager.showInfoOnce('已打开Sci-Hub下载窗口，如果下载失败请尝试使用下拉菜单中的其他链接');
      }
    } catch (error) {
      console.error('打开Sci-Hub失败:', error);
      errorManager.showErrorOnce('无法从Sci-Hub获取PDF，请手动尝试下面的链接');
    }
  };

  // 查看摘要
  const viewAbstract = (id: number) => {
    setViewAbstractId(id);
  };

  // 关闭摘要弹窗
  const closeAbstractModal = () => {
    setViewAbstractId(null);
  };

  // 处理随机推荐类别变更
  const handleRandomCategoryChange = (value: string) => {
    setRandomCategory(value);
    fetchRandomRecommendations(value !== '全部' ? value : undefined);
  };

  // 从文献链接直接访问或下载
  const handleVisitOriginalSource = (paper: Paper) => {
    // 优先使用论文自带的链接
    if (paper.url) {
      window.open(paper.url, '_blank');
      errorManager.showInfoOnce('正在打开原始文献链接...');
    } else if (paper.doi) {
      // 如果没有URL但有DOI，构建DOI链接
      const doiUrl = `https://doi.org/${paper.doi}`;
      window.open(doiUrl, '_blank');
      errorManager.showInfoOnce('正在打开DOI链接，可能需要购买或订阅...');
    } else {
      errorManager.showErrorOnce('该文献没有可用的原始链接');
    }
  };

  // 根据文献情况选择合适的下载方式
  const handleDownload = (paper: Paper) => {
    // 如果有DOI，尝试从Sci-Hub下载
    if (paper.doi) {
      handleOpenSciHub(paper.doi);
    } else {
      errorManager.showErrorOnce('该文献没有DOI信息，无法从Sci-Hub下载');
    }
  };

  // 获取下载菜单项
  const getDownloadMenuItems = (paper: Paper) => {
    const items = [];
    
    // 如果有原始URL
    if (paper.url) {
      items.push(
        <Menu.Item key="original" onClick={() => window.open(paper.url, '_blank')}>
          原始链接
        </Menu.Item>
      );
    }
    
    // 如果有DOI
    if (paper.doi) {
      items.push(
        <Menu.Item key="doi" onClick={() => window.open(`https://doi.org/${paper.doi}`, '_blank')}>
          DOI原始链接
        </Menu.Item>
      );
      
      // 添加SciHub链接
      scihubApi.getDirectLinks(paper.doi).map((url, index) => (
        items.push(
          <Menu.Item key={`scihub-${index}`} onClick={() => window.open(url, '_blank')}>
            {`SciHub链接 ${index + 1}`}
          </Menu.Item>
        )
      ));
    }
    
    return items;
  };

  // 组件初始化时加载数据
  useEffect(() => {
    // 获取推荐
    fetchRecommendations();
    
    // 获取随机推荐
    fetchRandomRecommendations();
    
    // 获取最新论文（始终获取计算机领域）
    fetchLatestPapers();
  }, []);

  // 渲染推荐列表
  const renderRecommendations = (recommendations: Recommendation[]) => {
    if (loading && recommendations === randomRecommendations && randomLoading) {
      return <Spin size="large" />;
    }

    if (!recommendations || recommendations.length === 0) {
      return (
        <Empty
          description="暂无推荐内容"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={recommendations === randomRecommendations ? forceRefreshRandomRecommendations : forceRefreshRecommendations}>
            获取推荐
          </Button>
        </Empty>
      );
    }

    // 确保recommendations是数组
    if (!Array.isArray(recommendations)) {
      console.error('推荐列表不是数组:', recommendations);
      return <Alert message="数据格式错误" description="推荐列表格式不正确" type="error" />;
    }

    return (
      <>
        <Row gutter={[16, 16]}>
          {recommendations.map((rec) => (
            <Col xs={24} sm={24} md={12} lg={8} key={rec.id}>
              <Card
                title={
                  <div style={{ height: '60px', overflow: 'hidden' }}>
                    <Text strong ellipsis>
                      {rec.paper.title}
                    </Text>
                  </div>
                }
                actions={[
                  <Button 
                    type="text" 
                    icon={<EyeOutlined />} 
                    onClick={() => viewAbstract(rec.paper.id)}
                  >
                    摘要
                  </Button>,
                  <Button 
                    type="text" 
                    icon={<DownloadOutlined />} 
                    onClick={() => handleDownload(rec.paper)}
                  >
                    下载
                  </Button>
                ]}
                style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              >
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ marginBottom: '8px', height: '48px', overflow: 'hidden' }}>
                    <Text type="secondary" ellipsis>
                      {rec.paper.authors}
                    </Text>
                  </div>
                  <div>
                    <Space wrap>
                      <Tag color="green">相关性 {(rec.score * 100).toFixed(0)}%</Tag>
                      {rec.paper.doi && <Tag color="blue">DOI: {rec.paper.doi.substring(0, 10)}...</Tag>}
                      {rec.paper.source && <Tag color="orange">{rec.paper.source}</Tag>}
                    </Space>
                  </div>
                </div>
                <Divider style={{ margin: '8px 0' }} />
                <Paragraph
                  type="secondary"
                  ellipsis
                  style={{ fontSize: '12px', marginBottom: '8px' }}
                >
                  推荐理由: {rec.reason}
                </Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </>
    );
  };

  // 渲染最新论文列表
  const renderLatestPapers = () => {
    if (loading) {
      return <Spin size="large" />;
    }

    if (latestPapers.length === 0) {
      return (
        <Empty
          description="暂无最新论文"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={forceRefreshLatestPapers}>
            刷新论文
          </Button>
        </Empty>
      );
    }

    return (
      <>
        <Row gutter={[16, 16]}>
          {latestPapers.map((paper) => (
            <Col xs={24} sm={24} md={12} lg={8} key={paper.id}>
              <Card
                title={
                  <div style={{ height: '60px', overflow: 'hidden' }}>
                    <Text strong ellipsis>
                      {paper.title}
                    </Text>
                  </div>
                }
                extra={
                  paper.journal && (
                    <Tag color={
                      paper.journal.ranking === 'A+' ? 'magenta' :
                      paper.journal.ranking === 'A' ? 'red' :
                      paper.journal.ranking === 'B' ? 'orange' : 'blue'
                    }>
                      {paper.journal.abbreviation} ({paper.journal.ranking})
                    </Tag>
                  )
                }
                actions={[
                  <Button 
                    type="text" 
                    icon={<EyeOutlined />} 
                    onClick={() => viewAbstract(paper.id)}
                  >
                    摘要
                  </Button>,
                  <Button 
                    type="text" 
                    icon={<DownloadOutlined />} 
                    onClick={() => handleDownload(paper)}
                  >
                    下载
                  </Button>
                ]}
                style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              >
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ marginBottom: '8px', height: '48px', overflow: 'hidden' }}>
                    <Text type="secondary" ellipsis>
                      {paper.authors}
                    </Text>
                  </div>
                  <div>
                    <Space wrap>
                      {paper.journal?.category && <Tag color="purple">{paper.journal.category}</Tag>}
                      {paper.doi && <Tag color="blue">DOI: {paper.doi.substring(0, 10)}...</Tag>}
                      {paper.publication_date && (
                        <Tag color="cyan">
                          {dayjs(paper.publication_date).format('YYYY/MM/DD')}
                        </Tag>
                      )}
                    </Space>
                  </div>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </>
    );
  };

  // 获取当前查看的论文
  const getCurrentPaper = () => {
    if (!viewAbstractId) return null;
    
    // 从推荐中查找
    const fromRecs = recommendations.find(r => r.paper.id === viewAbstractId);
    if (fromRecs) return fromRecs.paper;
    
    // 从随机推荐中查找
    const fromRandomRecs = randomRecommendations.find(r => r.paper.id === viewAbstractId);
    if (fromRandomRecs) return fromRandomRecs.paper;
    
    // 从最新论文中查找
    return latestPapers.find(p => p.id === viewAbstractId);
  };

  const currentPaper = getCurrentPaper();

  return (
    <div style={{ padding: '24px' }}>
      <Tabs defaultActiveKey="recommended">
        <TabPane 
          tab={
            <span>
              <StarOutlined />
              个性化推荐
            </span>
          } 
          key="recommended"
        >
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
            <Title level={4}>
              <BookOutlined /> 为您推荐的论文
            </Title>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              loading={refreshingRecommendations}
              onClick={forceRefreshRecommendations}
            >
              刷新推荐
            </Button>
          </div>
          {renderRecommendations(recommendations)}
        </TabPane>
        <TabPane 
          tab={
            <span>
              <ThunderboltOutlined />
              随机推荐
            </span>
          } 
          key="random"
        >
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={4}>
              <ThunderboltOutlined /> 领域随机推荐
            </Title>
            <Space>
              <Select
                style={{ width: 150 }}
                value={randomCategory}
                onChange={handleRandomCategoryChange}
                placeholder="选择学科领域"
              >
                {categories.map(category => (
                  <Option key={category} value={category}>{category}</Option>
                ))}
              </Select>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                loading={randomLoading}
                onClick={forceRefreshRandomRecommendations}
              >
                刷新推荐
              </Button>
            </Space>
          </div>
          {renderRecommendations(randomRecommendations)}
        </TabPane>
        <TabPane 
          tab={
            <span>
              <FileSearchOutlined />
              最新论文
            </span>
          } 
          key="latest"
        >
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={4}>
              <FileSearchOutlined /> 顶级期刊最新论文
            </Title>
            <Space>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                loading={refreshingLatestPapers}
                onClick={forceRefreshLatestPapers}
              >
                刷新论文
              </Button>
            </Space>
          </div>
          {renderLatestPapers()}
        </TabPane>
      </Tabs>

      <Modal
        title={currentPaper?.title}
        open={Boolean(viewAbstractId)}
        onCancel={closeAbstractModal}
        footer={[
          <Button key="close" onClick={closeAbstractModal}>
            关闭
          </Button>,
          currentPaper && (
            <Dropdown 
              key="download"
              overlay={
                <Menu>
                  {getDownloadMenuItems(currentPaper)}
                </Menu>
              }
            >
              <Button 
                type="primary" 
                onClick={() => handleDownload(currentPaper)}
                icon={<DownloadOutlined />}
              >
                下载/访问 <DownOutlined />
              </Button>
            </Dropdown>
          ),
        ]}
        width={720}
      >
        {currentPaper && (
          <>
            <Paragraph>
              <Text strong>作者:</Text> {currentPaper.authors}
            </Paragraph>
            {currentPaper.publication_date && (
              <Paragraph>
                <Text strong>发布日期:</Text> {dayjs(currentPaper.publication_date).format('YYYY/MM/DD')}
              </Paragraph>
            )}
            {currentPaper.doi && (
              <Paragraph>
                <Text strong>DOI:</Text> {currentPaper.doi}
              </Paragraph>
            )}
            {currentPaper && (
              <Alert
                style={{ marginBottom: 16 }}
                message="关于文献访问"
                description={
                  currentPaper.url 
                    ? "系统将优先使用文献的原始链接进行访问。您可以通过下拉菜单选择其他访问方式。" 
                    : (currentPaper.doi 
                        ? (new Date(currentPaper.publication_date || "").getFullYear() >= 2021 
                            ? "该文献较新，优先使用DOI链接访问，可能需要机构访问权限或购买。您也可以尝试SciHub链接。"
                            : "该文献可能可以通过SciHub访问，如果无法下载，请尝试使用其他链接。")
                        : "该文献没有提供下载链接，请通过其他渠道获取。")
                }
                type="info"
                showIcon
              />
            )}
            <Divider />
            <Paragraph>
              <Text strong>摘要:</Text>
            </Paragraph>
            <Paragraph style={{ textAlign: 'justify' }}>
              {currentPaper.abstract || '暂无摘要'}
            </Paragraph>
          </>
        )}
      </Modal>
    </div>
  );
};

export default Recommendations; 