import React, { useState, useEffect } from 'react';
import { Table, Button, Form, Select, Radio, Slider, Modal, Alert, Divider, Progress, Empty, Spin, message, Typography, theme } from 'antd';
import { knowledgeGraphApi, userApi } from '../services/api';
import { InfoCircleOutlined } from '@ant-design/icons';

const { Option } = Select;
const { Title, Paragraph, Text } = Typography;

interface Paper {
  id: number;
  title: string;
  authors: string;
  year?: number;
  abstract?: string;
}

interface SimilarPaper {
  paper_id: number;
  title: string;
  authors: string;
  year?: number;
  similarity: number;
  shared_concepts: number;
  concept_similarity?: number;
  title_similarity?: number;
  author_similarity?: number;
  venue_similarity?: number;
  year_similarity?: number;
}

interface SimilarityRecord {
  id: number;
  source_paper_id: number;
  source_paper_title: string;
  target_paper_id?: number;
  target_paper_title?: string;
  compare_mode: 'all' | 'specific';
  similarity_threshold?: number;
  created_at: string;
}

const PaperSimilarity: React.FC = () => {
  // 添加主题支持
  const { token } = theme.useToken();
  
  const [userPapers, setUserPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [similarPapers, setSimilarPapers] = useState<SimilarPaper[]>([]);
  const [calculatingSimilarity, setCalculatingSimilarity] = useState(false);
  const [simPaperId, setSimPaperId] = useState<number | null>(null);
  const [compareMode, setCompareMode] = useState<'all' | 'specific'>('all');
  const [comparePaperId, setComparePaperId] = useState<number | null>(null);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.3);
  const [similarityForm] = Form.useForm();
  
  // 新增状态用于详细相似度模态框
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedPaperDetail, setSelectedPaperDetail] = useState<SimilarPaper | null>(null);
  
  // 新增历史记录状态
  const [historyRecords, setHistoryRecords] = useState<SimilarityRecord[]>([]);
  const [historyVisible, setHistoryVisible] = useState(false);

  useEffect(() => {
    fetchUserPapers();
    // 这里可以添加获取历史记录的函数调用
    // fetchHistoryRecords();
  }, []);

  const fetchUserPapers = async () => {
    setLoading(true);
    try {
      const response = await userApi.getUserPapers();
      if (response.data) {
        setUserPapers(response.data);
      }
    } catch (error) {
      console.error('获取用户论文失败', error);
      message.error('获取用户论文失败');
    } finally {
      setLoading(false);
    }
  };

  // 计算论文相似度
  const handleCalculateSimilarity = async () => {
    if (!simPaperId) {
      message.error('请选择一篇论文');
      return;
    }

    if (compareMode === 'specific' && !comparePaperId) {
      message.error('请选择要比较的论文');
      return;
    }

    setCalculatingSimilarity(true);
    try {
      let response;
      
      if (compareMode === 'all') {
        // 与所有论文比较
        response = await knowledgeGraphApi.calculatePaperSimilarity(
          simPaperId,
          similarityThreshold
        );
      } else {
        // 与特定论文比较
        response = await knowledgeGraphApi.calculateTwoPapersSimilarity(
          simPaperId,
          comparePaperId as number
        );
      }
      
      if (response.data && Array.isArray(response.data)) {
        setSimilarPapers(response.data);
        if (response.data.length === 0) {
          message.info('未找到相似度达到阈值的论文');
        }
      } else if (response.data && !Array.isArray(response.data)) {
        // 处理单个论文比较的结果
        const detailedSimilarity = response.data;
        const result = [{
          paper_id: comparePaperId as number,
          title: userPapers.find(p => p.id === comparePaperId)?.title || '',
          authors: userPapers.find(p => p.id === comparePaperId)?.authors || '',
          year: userPapers.find(p => p.id === comparePaperId)?.year,
          similarity: detailedSimilarity.similarity,
          shared_concepts: detailedSimilarity.shared_concepts,
          // 新增详细相似度指标
          concept_similarity: detailedSimilarity.concept_similarity,
          title_similarity: detailedSimilarity.title_similarity,
          author_similarity: detailedSimilarity.author_similarity,
          venue_similarity: detailedSimilarity.venue_similarity,
          year_similarity: detailedSimilarity.year_similarity
        }];
        setSimilarPapers(result);
        
        // 显示详细相似度信息的提示
        if (compareMode === 'specific') {
          message.info('已计算两篇论文的相似度，请查看详细结果');
        }
      }
      
      // 在这里应该添加保存历史记录的逻辑
      // saveHistoryRecord();
      
    } catch (error) {
      console.error('计算论文相似度失败', error);
      message.error('计算论文相似度失败');
    } finally {
      setCalculatingSimilarity(false);
    }
  };

  // 渲染相似论文的表格列定义
  const similarPapersColumns = [
    {
      title: '论文标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string, record: SimilarPaper) => (
        <a href={`/papers/${record.paper_id}`} target="_blank" rel="noopener noreferrer">
          {text}
        </a>
      )
    },
    {
      title: '作者',
      dataIndex: 'authors',
      key: 'authors',
      width: 180,
      ellipsis: true,
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: 90,
      align: 'center' as 'center',
    },
    {
      title: '综合相似度',
      dataIndex: 'similarity',
      key: 'similarity',
      width: 150,
      align: 'center' as 'center',
      render: (similarity: number) => (
        <div style={{ padding: '0 4px' }}>
          <Progress 
            percent={Number((similarity * 100).toFixed(1))} 
            size="small" 
            status="active"
            strokeColor={{
              from: token.colorPrimary,
              to: token.colorSuccess,
            }}
            format={(percent) => `${percent?.toFixed(1)}%`}
            style={{ marginBottom: '4px' }}
          />
          <div style={{ 
            textAlign: 'center', 
            fontSize: '14px', 
            fontWeight: 'bold',
            color: similarity > 0.7 ? token.colorSuccess : 
                  similarity > 0.4 ? token.colorWarning : 
                  token.colorPrimary
          }}>
            {(similarity * 100).toFixed(1)}%
          </div>
        </div>
      ),
      sorter: (a: SimilarPaper, b: SimilarPaper) => a.similarity - b.similarity,
      defaultSortOrder: 'descend' as 'descend'
    },
    {
      title: '共享概念',
      dataIndex: 'shared_concepts',
      key: 'shared_concepts',
      width: 100,
      align: 'center' as 'center',
      render: (count: number) => (
        <div style={{ 
          backgroundColor: token.colorInfoBg,
          borderRadius: '16px',
          padding: '2px 8px',
          display: 'inline-block',
          color: token.colorInfo,
          fontWeight: 'bold'
        }}>
          {count}
        </div>
      )
    },
    {
      title: '详细分析',
      key: 'detailed_similarity',
      width: 120,
      align: 'center' as 'center',
      render: (text: string, record: SimilarPaper) => {
        // 如果没有详细相似度指标，则返回N/A
        if (record.concept_similarity === undefined) {
          return <Text type="secondary">N/A</Text>;
        }
        
        return (
          <Button 
            type="primary"
            size="small"
            onClick={() => {
              setSelectedPaperDetail(record);
              setDetailModalVisible(true);
            }}
          >
            查看详情
          </Button>
        );
      }
    }
  ];

  return (
    <div className="paper-similarity-container" style={{ padding: '24px' }}>
      <div className="page-header" style={{ marginBottom: '24px' }}>
        <Title level={2}>论文相似度分析</Title>
        <Paragraph>此功能可帮助您分析论文之间的相关性，并发现领域内的相似研究。</Paragraph>
      </div>
      
      <div className="tools-container" style={{ 
        backgroundColor: token.colorBgContainer,
        padding: '20px', 
        borderRadius: '8px', 
        marginBottom: '24px',
        boxShadow: token.boxShadow,
        border: `1px solid ${token.colorBorderSecondary}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <Title level={4} style={{ margin: 0 }}>计算相似度</Title>
          <Button 
            type="primary" 
            onClick={() => setHistoryVisible(true)}
            icon={<InfoCircleOutlined />}
          >
            查看历史记录
          </Button>
        </div>
        
        <Form
          form={similarityForm}
          layout="vertical"
          onFinish={handleCalculateSimilarity}
          initialValues={{ compareMode: 'all' }}
        >
          <div style={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: '24px',
            marginBottom: '24px' 
          }}>
            <Form.Item
              label="比较模式"
              name="compareMode"
              style={{ minWidth: '220px', marginBottom: '8px' }}
            >
              <Radio.Group 
                onChange={(e) => setCompareMode(e.target.value as 'all' | 'specific')}
                value={compareMode}
                style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}
              >
                <Radio.Button value="all" style={{ width: '100%', textAlign: 'center' }}>比较所有论文</Radio.Button>
                <Radio.Button value="specific" style={{ width: '100%', textAlign: 'center' }}>比较特定论文</Radio.Button>
              </Radio.Group>
            </Form.Item>
            
            <Form.Item
              label="源论文"
              style={{ 
                flex: '1', 
                minWidth: '300px', 
                marginBottom: '8px' 
              }}
            >
              <Select
                style={{ width: '100%' }} 
                placeholder="选择源论文"
                value={simPaperId}
                onChange={(value) => setSimPaperId(value)}
                showSearch
                optionFilterProp="children"
              >
                {userPapers.map(paper => (
                  <Option key={paper.id} value={paper.id}>
                    {paper.title}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            
            {compareMode === 'specific' && (
              <Form.Item
                label="目标论文"
                style={{ 
                  flex: '1', 
                  minWidth: '300px', 
                  marginBottom: '8px' 
                }}
              >
                <Select
                  style={{ width: '100%' }} 
                  placeholder="选择目标论文"
                  value={comparePaperId}
                  onChange={(value) => setComparePaperId(value)}
                  showSearch
                  optionFilterProp="children"
                >
                  {userPapers.filter(p => p.id !== simPaperId).map(paper => (
                    <Option key={paper.id} value={paper.id}>
                      {paper.title}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            )}
            
            {compareMode === 'all' && (
              <Form.Item
                label="相似度阈值"
                style={{ 
                  minWidth: '250px', 
                  flex: '1',
                  marginBottom: '8px' 
                }}
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.05}
                  value={similarityThreshold}
                  onChange={(val) => setSimilarityThreshold(val)}
                  marks={{
                    0: '0',
                    0.3: '0.3',
                    0.5: '0.5',
                    0.7: '0.7',
                    1: '1'
                  }}
                />
              </Form.Item>
            )}
          </div>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center',
            marginTop: '12px',
            marginBottom: '8px'
          }}>
            <Form.Item style={{ marginBottom: 0 }}>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={calculatingSimilarity}
                size="large"
                style={{ 
                  minWidth: '160px', 
                  height: '44px',
                  boxShadow: token.boxShadow
                }}
              >
                计算相似度
              </Button>
            </Form.Item>
          </div>
        </Form>
      </div>
      
      <div className="results-container" style={{ 
        backgroundColor: token.colorBgContainer,
        padding: '24px', 
        borderRadius: '8px',
        boxShadow: token.boxShadow,
        border: `1px solid ${token.colorBorderSecondary}`,
        marginTop: '24px'
      }}>
        <Title level={4} style={{ marginTop: 0, marginBottom: '20px' }}>分析结果</Title>
        
        {similarPapers.length > 0 ? (
          <>
            <Alert
              message="相似度说明"
              description={
                compareMode === 'specific' 
                  ? "下方显示了两篇论文的综合相似度，包括概念、标题、作者、期刊和年份等多个维度的对比。"
                  : "下方列出了与选中论文相似度高于阈值的论文，按相似度从高到低排序。"
              }
              type="info"
              showIcon
              style={{ marginBottom: '24px', borderRadius: '6px' }}
            />
            
            <Table
              dataSource={similarPapers}
              columns={similarPapersColumns}
              rowKey="paper_id"
              pagination={{ pageSize: 10 }}
              style={{ marginBottom: '16px' }}
              className="similar-papers-table"
            />
          </>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px',
            backgroundColor: token.colorBgContainer,
            borderRadius: '6px',
            border: `1px solid ${token.colorBorderSecondary}`
          }}>
            {calculatingSimilarity ? (
              <div style={{ padding: '30px' }}>
                <Spin tip="正在计算相似度..." size="large" />
              </div>
            ) : (
              <Empty 
                description={
                  <span style={{ color: token.colorTextSecondary }}>
                    尚未计算论文相似度，请在上方选择论文并点击计算按钮
                  </span>
                }
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                style={{ margin: '20px 0' }}
              />
            )}
          </div>
        )}
      </div>
      
      {/* 详细相似度模态框 */}
      <Modal
        title="详细相似度分析"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={600}
        centered
        style={{ top: 20 }}
        bodyStyle={{ padding: '24px' }}
      >
        {selectedPaperDetail && (
          <div>
            <div style={{ 
              backgroundColor: token.colorInfoBg, 
              padding: '16px', 
              borderRadius: '8px',
              marginBottom: '24px'
            }}>
              <div style={{ marginBottom: '12px' }}>
                <Text strong>论文:</Text> {selectedPaperDetail.title}
              </div>
              
              <div>
                <Text strong>作者:</Text> {selectedPaperDetail.authors}
                {selectedPaperDetail.year && (
                  <span style={{ marginLeft: '16px' }}>
                    <Text strong>年份:</Text> {selectedPaperDetail.year}
                  </span>
                )}
              </div>
            </div>
            
            <Title level={5} style={{ 
              marginBottom: '16px',
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
              paddingBottom: '8px'
            }}>
              相似度维度分析
            </Title>
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <Text strong>概念相似度:</Text>
                <Text style={{ 
                  fontWeight: 'bold',
                  color: (selectedPaperDetail.concept_similarity || 0) > 0.7 ? token.colorSuccess : 
                         (selectedPaperDetail.concept_similarity || 0) > 0.4 ? token.colorWarning : 
                         token.colorPrimary
                }}>
                  {((selectedPaperDetail.concept_similarity || 0) * 100).toFixed(1)}%
                </Text>
              </div>
              <Progress 
                percent={Number(((selectedPaperDetail.concept_similarity || 0) * 100).toFixed(1))} 
                size="small" 
                status="active"
                strokeColor={
                  (selectedPaperDetail.concept_similarity || 0) > 0.7 ? token.colorSuccess : 
                  (selectedPaperDetail.concept_similarity || 0) > 0.4 ? token.colorWarning : 
                  token.colorPrimary
                }
              />
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <Text strong>标题相似度:</Text>
                <Text style={{ 
                  fontWeight: 'bold',
                  color: (selectedPaperDetail.title_similarity || 0) > 0.7 ? token.colorSuccess : 
                         (selectedPaperDetail.title_similarity || 0) > 0.4 ? token.colorWarning : 
                         token.colorPrimary
                }}>
                  {((selectedPaperDetail.title_similarity || 0) * 100).toFixed(1)}%
                </Text>
              </div>
              <Progress 
                percent={Number(((selectedPaperDetail.title_similarity || 0) * 100).toFixed(1))} 
                size="small" 
                status="active"
                strokeColor={
                  (selectedPaperDetail.title_similarity || 0) > 0.7 ? token.colorSuccess : 
                  (selectedPaperDetail.title_similarity || 0) > 0.4 ? token.colorWarning : 
                  token.colorPrimary
                }
              />
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <Text strong>作者相似度:</Text>
                <Text style={{ 
                  fontWeight: 'bold',
                  color: (selectedPaperDetail.author_similarity || 0) > 0.7 ? token.colorSuccess : 
                         (selectedPaperDetail.author_similarity || 0) > 0.4 ? token.colorWarning : 
                         token.colorPrimary
                }}>
                  {((selectedPaperDetail.author_similarity || 0) * 100).toFixed(1)}%
                </Text>
              </div>
              <Progress 
                percent={Number(((selectedPaperDetail.author_similarity || 0) * 100).toFixed(1))} 
                size="small" 
                status="active"
                strokeColor={
                  (selectedPaperDetail.author_similarity || 0) > 0.7 ? token.colorSuccess : 
                  (selectedPaperDetail.author_similarity || 0) > 0.4 ? token.colorWarning : 
                  token.colorPrimary
                }
              />
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <Text strong>期刊相似度:</Text>
                <Text style={{ 
                  fontWeight: 'bold',
                  color: (selectedPaperDetail.venue_similarity || 0) > 0.7 ? token.colorSuccess : 
                         (selectedPaperDetail.venue_similarity || 0) > 0.4 ? token.colorWarning : 
                         token.colorPrimary
                }}>
                  {((selectedPaperDetail.venue_similarity || 0) * 100).toFixed(1)}%
                </Text>
              </div>
              <Progress 
                percent={Number(((selectedPaperDetail.venue_similarity || 0) * 100).toFixed(1))} 
                size="small" 
                status="active"
                strokeColor={
                  (selectedPaperDetail.venue_similarity || 0) > 0.7 ? token.colorSuccess : 
                  (selectedPaperDetail.venue_similarity || 0) > 0.4 ? token.colorWarning : 
                  token.colorPrimary
                }
              />
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <Text strong>年份相似度:</Text>
                <Text style={{ 
                  fontWeight: 'bold',
                  color: (selectedPaperDetail.year_similarity || 0) > 0.7 ? token.colorSuccess : 
                         (selectedPaperDetail.year_similarity || 0) > 0.4 ? token.colorWarning : 
                         token.colorPrimary
                }}>
                  {((selectedPaperDetail.year_similarity || 0) * 100).toFixed(1)}%
                </Text>
              </div>
              <Progress 
                percent={Number(((selectedPaperDetail.year_similarity || 0) * 100).toFixed(1))} 
                size="small" 
                status="active"
                strokeColor={
                  (selectedPaperDetail.year_similarity || 0) > 0.7 ? token.colorSuccess : 
                  (selectedPaperDetail.year_similarity || 0) > 0.4 ? token.colorWarning : 
                  token.colorPrimary
                }
              />
            </div>
            
            <div style={{ 
              backgroundColor: token.colorBgContainer,
              border: `1px solid ${token.colorBorderSecondary}`,
              borderRadius: '8px',
              padding: '16px',
              marginTop: '24px',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <div>
                <Text strong style={{ fontSize: '16px' }}>共享概念数:</Text> 
                <Text style={{ 
                  fontSize: '16px',
                  marginLeft: '8px',
                  backgroundColor: token.colorInfoBg,
                  color: token.colorInfo,
                  padding: '2px 10px',
                  borderRadius: '12px',
                  fontWeight: 'bold'
                }}>
                  {selectedPaperDetail.shared_concepts}
                </Text>
              </div>
              
              <div>
                <Text strong style={{ fontSize: '16px' }}>综合相似度:</Text> 
                <Text style={{ 
                  fontSize: '16px',
                  marginLeft: '8px',
                  fontWeight: 'bold',
                  color: selectedPaperDetail.similarity > 0.7 ? token.colorSuccess : 
                         selectedPaperDetail.similarity > 0.4 ? token.colorWarning : 
                         token.colorPrimary
                }}>
                  {(selectedPaperDetail.similarity * 100).toFixed(1)}%
                </Text>
              </div>
            </div>
          </div>
        )}
      </Modal>
      
      {/* 历史记录模态框 */}
      <Modal
        title="相似度分析历史记录"
        open={historyVisible}
        onCancel={() => setHistoryVisible(false)}
        footer={null}
        width={800}
      >
        {historyRecords.length > 0 ? (
          <Table
            dataSource={historyRecords}
            columns={[
              {
                title: '源论文',
                dataIndex: 'source_paper_title',
                key: 'source_paper_title',
                ellipsis: true,
              },
              {
                title: '目标论文',
                dataIndex: 'target_paper_title',
                key: 'target_paper_title',
                ellipsis: true,
                render: (text, record) => {
                  return record.compare_mode === 'specific' ? text : '全部论文';
                }
              },
              {
                title: '比较模式',
                dataIndex: 'compare_mode',
                key: 'compare_mode',
                render: (text) => text === 'all' ? '全部论文' : '特定论文'
              },
              {
                title: '阈值',
                dataIndex: 'similarity_threshold',
                key: 'similarity_threshold',
                render: (text, record) => {
                  return record.compare_mode === 'all' ? text : 'N/A';
                }
              },
              {
                title: '分析时间',
                dataIndex: 'created_at',
                key: 'created_at',
              },
              {
                title: '操作',
                key: 'action',
                render: (_, record) => (
                  <Button 
                    type="link"
                    onClick={() => {
                      // 重新加载该记录的分析结果
                      setSimPaperId(record.source_paper_id);
                      setCompareMode(record.compare_mode);
                      if (record.compare_mode === 'specific' && record.target_paper_id) {
                        setComparePaperId(record.target_paper_id);
                      }
                      if (record.compare_mode === 'all' && record.similarity_threshold) {
                        setSimilarityThreshold(record.similarity_threshold);
                      }
                      setHistoryVisible(false);
                      // 调用计算函数
                      setTimeout(() => {
                        handleCalculateSimilarity();
                      }, 300);
                    }}
                  >
                    重新分析
                  </Button>
                )
              }
            ]}
            rowKey="id"
            pagination={{ pageSize: 5 }}
          />
        ) : (
          <Empty 
            description={
              <span style={{ color: token.colorTextSecondary }}>
                暂无相似度分析历史记录
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Modal>
    </div>
  );
};

export default PaperSimilarity; 