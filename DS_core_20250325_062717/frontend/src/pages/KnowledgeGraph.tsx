import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Card, 
  Typography, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message, 
  Spin, 
  Tabs, 
  Table, 
  Tag, 
  Space, 
  InputNumber,
  List,
  Collapse,
  Alert,
  Tooltip,
  Divider,
  Popconfirm,
  Radio,
  Progress,
  Slider,
  Layout,
  Row,
  Col,
  Descriptions,
  Empty,
  Dropdown,
  Steps,
  Timeline
} from 'antd';
import { knowledgeGraphApi, paperApi } from '../services/api';
import ForceGraph2D from 'react-force-graph-2d';
import {
  PlusOutlined,
  LinkOutlined,
  SearchOutlined,
  FileSearchOutlined,
  ReadOutlined,
  BulbOutlined,
  ExperimentOutlined,
  BranchesOutlined,
  EditOutlined,
  DeleteOutlined,
  MinusOutlined,
  FullscreenOutlined,
  EyeOutlined,
  ReloadOutlined,
  DownOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { Panel } = Collapse;
const { Content } = Layout;

interface GraphNode {
  id: string;
  name: string;
  color?: string;
  weight?: number;
  description?: string;
  category?: number;
}

interface GraphLink {
  source: string;
  target: string;
  label?: string;
  value?: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  stats?: {
    conceptCount: number;
    relationCount: number;
  };
  categories?: Array<{
    name: string;
    itemStyle: {
      color: string;
    }
  }>;
}

interface Concept {
  id: number;
  name: string;
  description?: string;
  weight?: number;
  category?: number;
}

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

interface ReadingPathConcept {
  id: number;
  name: string;
  description?: string;
  related_papers: Array<{id: number, title: string, authors: string}>;
}

interface ReadingPath {
  start_concept: string;
  target_concept: string;
  path_length: number;
  concepts: ReadingPathConcept[];
  path: ReadingPathConcept[];
}

interface ForceGraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface Relation {
  id: number;
  source_id: string;
  target_id: string;
  relation_type: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface CreateRelation {
  source_id: string;
  target_id: string;
  relation_type: string;
  description: string;
}

const KnowledgeGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [addConceptVisible, setAddConceptVisible] = useState(false);
  const [addRelationVisible, setAddRelationVisible] = useState(false);
  const [extractConceptsVisible, setExtractConceptsVisible] = useState(false);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [userPapers, setUserPapers] = useState<Paper[]>([]);
  const [selectedPaperId, setSelectedPaperId] = useState<number | null>(null);
  const [extractingConcepts, setExtractingConcepts] = useState(false);
  const [activeTabKey, setActiveTabKey] = useState('1');
  const [similarPapers, setSimilarPapers] = useState<SimilarPaper[]>([]);
  const [calculatingSimilarity, setCalculatingSimilarity] = useState(false);
  const [simPaperId, setSimPaperId] = useState<number | null>(null);
  const [compareMode, setCompareMode] = useState<'all' | 'specific'>('all');
  const [comparePaperId, setComparePaperId] = useState<number | null>(null);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.3);
  const [calculateSimilarityVisible, setCalculateSimilarityVisible] = useState(false);
  const [readingPathVisible, setReadingPathVisible] = useState(false);
  const [selectedConceptId, setSelectedConceptId] = useState<number | null>(null);
  const [readingPaths, setReadingPaths] = useState<ReadingPath[]>([]);
  const [loadingReadingPath, setLoadingReadingPath] = useState(false);
  const [form] = Form.useForm();
  const [relationForm] = Form.useForm();
  const [extractForm] = Form.useForm();
  const [similarityForm] = Form.useForm();
  const [readingPathForm] = Form.useForm();
  const graphRef = useRef<any>(null);
  
  // 新增状态
  const [editConceptVisible, setEditConceptVisible] = useState(false);
  const [editingConcept, setEditingConcept] = useState<Concept | null>(null);
  const [editForm] = Form.useForm();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [nodeDetailVisible, setNodeDetailVisible] = useState(false);

  // 新增状态用于详细相似度模态框
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedPaperDetail, setSelectedPaperDetail] = useState<SimilarPaper | null>(null);

  // 添加新状态用于图谱配置
  const [showMinimap, setShowMinimap] = useState(false);
  const minimapRef = useRef<HTMLCanvasElement>(null);

  // 简化图谱配置状态
  const [graphConfig, setGraphConfig] = useState({
    nodeSizeMultiplier: 1,
    linkStrength: 0.4
  });

  // 添加视图状态
  const [viewState, setViewState] = useState({
    scale: 1,
    x: 0,
    y: 0
  });

  // 添加图例详情模态框状态
  const [legendModalVisible, setLegendModalVisible] = useState(false);

  // 添加新状态用于记录当前的缩放状态
  const [currentZoom, setCurrentZoom] = useState(1);

  // 记录当前搜索文本
  const [searchText, setSearchText] = useState<string>('');
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());

  // 添加容器尺寸相关变量
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState<number>(800);
  const [height, setHeight] = useState<number>(600);

  // 添加调整尺寸的处理函数和副作用
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { offsetWidth, offsetHeight } = containerRef.current;
        setWidth(offsetWidth);
        setHeight(offsetHeight);
      }
    };

    // 初始化尺寸
    updateDimensions();

    // 监听窗口大小变化
    window.addEventListener('resize', updateDimensions);

    // 清理函数
    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  useEffect(() => {
    fetchGraphData();
    fetchConcepts();
    fetchUserPapers();
  }, []);

  const fetchGraphData = async () => {
    setLoading(true);
    
    // 在加载前保存当前的视图状态
    if (graphRef.current) {
      const currentZoomLevel = graphRef.current.zoom();
      const currentCenterPos = graphRef.current.centerAt();
      
      setViewState({
        scale: currentZoomLevel,
        x: currentCenterPos?.x || 0,
        y: currentCenterPos?.y || 0
      });
    }
    
    try {
      const response = await knowledgeGraphApi.getGraph();
      
      // 确保数据是正确的格式
      if (response.data && 
          response.data.nodes && Array.isArray(response.data.nodes) && 
          response.data.links && Array.isArray(response.data.links)) {
        
        // 增强节点数据
        const enhancedNodes = response.data.nodes.map((node: any) => {
          // 为不同类型节点分配颜色
          let nodeColor = '#1890ff';
          let nodeSize = 50;
          
          // 根据节点类型或属性设置不同的颜色
          if (node.category === 0) {
            nodeColor = '#1890ff'; // 基础概念 - 蓝色
            nodeSize = 50;
          } else if (node.category === 1) {
            nodeColor = '#52c41a'; // 扩展概念 - 绿色
            nodeSize = 45;
          } else if (node.category === 2) {
            nodeColor = '#722ed1'; // 主题概念 - 紫色
            nodeSize = 60;
          }
          
          // 如果有连接数，调整大小
          if (node.symbolSize) {
            nodeSize = Math.max(30, Math.min(80, node.symbolSize));
          }
          
          return {
            ...node,
            color: nodeColor,
            symbolSize: nodeSize,
          };
        });
        
        // 增强连接数据
        const enhancedLinks = response.data.links.map((link: any) => {
          return {
            ...link,
            // 根据权重设定线条粗细
            width: link.weight ? Math.max(1, Math.min(5, link.weight * 2)) : 1,
            // 设置连接曲率以避免重叠
            curvature: 0.2
          };
        });
        
        setGraphData({
          nodes: enhancedNodes,
          links: enhancedLinks
        });
      } else {
        console.warn('知识图谱数据格式不正确:', response.data);
        setGraphData({ nodes: [], links: [] });
      }
    } catch (error) {
      console.error('获取知识图谱数据失败', error);
      message.error('获取知识图谱数据失败');
      setGraphData({ nodes: [], links: [] });
    } finally {
      setLoading(false);
      
      // 数据加载完成后，恢复之前的视图状态，而不是自动缩放
      setTimeout(() => {
        if (graphRef.current && viewState && viewState.scale > 0) {
          // 不使用zoomToFit自动缩放，而是恢复用户上次的视图状态
          // 除非是第一次加载（viewState.scale <= 0）
          graphRef.current.zoom(viewState.scale, 0);
          if (viewState.x !== 0 || viewState.y !== 0) {
            graphRef.current.centerAt(viewState.x, viewState.y, 0);
          }
        }
      }, 100);
    }
  };

  const fetchConcepts = async () => {
    try {
      const response = await knowledgeGraphApi.getConcepts();
      
      // 确保数据是数组
      if (response.data && Array.isArray(response.data)) {
        setConcepts(response.data);
      } else if (response.data && response.data.concepts && Array.isArray(response.data.concepts)) {
        setConcepts(response.data.concepts);
      } else {
        console.warn('概念数据格式不正确:', response.data);
        setConcepts([]);
      }
    } catch (error) {
      console.error('获取概念列表失败', error);
      setConcepts([]);
    }
  };

  const fetchUserPapers = async () => {
    try {
      const response = await paperApi.getPapers();
      if (response.data && Array.isArray(response.data)) {
        setUserPapers(response.data);
      }
    } catch (error) {
      console.error('获取用户论文列表失败', error);
    }
  };

  const handleAddConcept = async (values: any) => {
    try {
      await knowledgeGraphApi.createConcept(values);
      message.success('概念添加成功');
      setAddConceptVisible(false);
      form.resetFields();
      fetchGraphData();
      fetchConcepts();
    } catch (error) {
      console.error('添加概念失败', error);
      message.error('添加概念失败');
    }
  };

  const handleAddRelation = async (values: any) => {
    try {
      await knowledgeGraphApi.createRelation({
        source_id: values.source,
        target_id: values.target,
        relation_type: values.relation_type,
        description: values.description || ''
      } as CreateRelation);
      message.success('关系添加成功');
      setAddRelationVisible(false);
      relationForm.resetFields();
      fetchGraphData();
    } catch (error) {
      message.error('添加关系失败');
    }
  };

  const handleExtractConcepts = async () => {
    if (!selectedPaperId) {
      message.error('请选择一篇论文');
      return;
    }

    setExtractingConcepts(true);
    try {
      const response = await knowledgeGraphApi.extractConcepts(selectedPaperId);
      if (response.data && response.data.extracted_concepts) {
        message.success(`成功从论文中提取了 ${response.data.extracted_concepts.length} 个概念`);
        fetchGraphData();
        fetchConcepts();
        setExtractConceptsVisible(false);
        extractForm.resetFields();
      }
    } catch (error) {
      console.error('从论文中提取概念失败', error);
      message.error('从论文中提取概念失败');
    } finally {
      setExtractingConcepts(false);
    }
  };

  const handleBatchExtractConcepts = async () => {
    try {
      setLoading(true);
      const response = await knowledgeGraphApi.batchExtractConcepts();
      if (response.data && response.data.processed_count) {
        message.success(`批量处理了 ${response.data.processed_count} 篇论文，提取了概念并建立了关系`);
        fetchGraphData();
        fetchConcepts();
      }
    } catch (error) {
      console.error('批量提取概念失败', error);
      message.error('批量提取概念失败');
    } finally {
      setLoading(false);
    }
  };

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
    } catch (error) {
      console.error('计算论文相似度失败', error);
      message.error('计算论文相似度失败');
    } finally {
      setCalculatingSimilarity(false);
    }
  };

  const handleGetReadingPath = async () => {
    if (!selectedConceptId) {
      message.error('请选择一个目标概念');
      return;
    }

    setLoadingReadingPath(true);
    try {
      const response = await knowledgeGraphApi.getReadingPath(selectedConceptId);
      if (response.data && response.data.learning_paths) {
        setReadingPaths(response.data.learning_paths);
        if (response.data.learning_paths.length === 0) {
          message.info('未找到通往该概念的学习路径');
        }
      }
    } catch (error) {
      console.error('获取学习路径失败', error);
      message.error('获取学习路径失败');
    } finally {
      setLoadingReadingPath(false);
    }
  };

  // 渲染相似论文的表格列定义
  const similarPapersColumns = [
    {
      title: '论文标题',
      dataIndex: 'title',
      key: 'title',
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
      width: 200,
      ellipsis: true,
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: 100,
    },
    {
      title: '综合相似度',
      dataIndex: 'similarity',
      key: 'similarity',
      width: 120,
      render: (similarity: number) => (
        <span>
          <Progress 
            percent={Number((similarity * 100).toFixed(1))} 
            size="small" 
            status="active"
            strokeColor={{
              from: '#108ee9',
              to: '#87d068',
            }}
          />
          {(similarity * 100).toFixed(1)}%
        </span>
      ),
      sorter: (a: SimilarPaper, b: SimilarPaper) => a.similarity - b.similarity,
      defaultSortOrder: 'descend' as 'descend'
    },
    {
      title: '共享概念数',
      dataIndex: 'shared_concepts',
      key: 'shared_concepts',
      width: 120
    },
    {
      title: '详细相似度',
      key: 'detailed_similarity',
      width: 120,
      render: (text: string, record: SimilarPaper) => {
        // 如果没有详细相似度指标，则返回N/A
        if (record.concept_similarity === undefined) {
          return <span>N/A</span>;
        }
        
        return (
          <Button 
            type="link"
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

  // 添加状态变量以正确保存和显示相关论文
  const [selectedNodePapers, setSelectedNodePapers] = useState<any[]>([]);

  // 修改节点点击处理函数，确保正确获取节点详情和相关论文
  const handleNodeClick = useCallback(async (node: GraphNode) => {
    setSelectedNode(node);
    setNodeDetailVisible(true);
    
    // 保存当前的缩放级别和位置，以便稍后恢复
    if (graphRef.current) {
      const currentZoomLevel = graphRef.current.zoom();
      const currentCenterPos = graphRef.current.centerAt();
      
      // 存储这些值，以便在操作后恢复
      setViewState({
        scale: currentZoomLevel,
        x: currentCenterPos?.x || 0,
        y: currentCenterPos?.y || 0
      });
    }
    
    // 获取概念详情，包括相关论文
    try {
      const conceptId = parseInt(node.id);
      const conceptData = await getConceptDetail(conceptId);
      
      // 获取相关论文
      try {
        const papersResponse = await knowledgeGraphApi.getConceptPapers(conceptId);
        if (papersResponse && papersResponse.data && Array.isArray(papersResponse.data)) {
          setSelectedNodePapers(papersResponse.data);
        } else {
          setSelectedNodePapers([]);
        }
      } catch (error) {
        console.error("获取概念相关论文失败", error);
        setSelectedNodePapers([]);
      }
    } catch (error) {
      console.error("获取概念详情失败", error);
    }
  }, []);

  // 修改获取概念详情函数，不再处理相关论文
  const getConceptDetail = async (id: number): Promise<Concept | null> => {
    try {
      const response = await knowledgeGraphApi.getConceptDetail(id);
      if (response && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error("获取概念详情失败", error);
      message.error("获取概念详情失败");
      return null;
    }
  };

  // 处理编辑概念
  const handleEditConcept = async () => {
    if (!selectedNode) return;
    
    try {
      // 获取概念详情
      const conceptData = await getConceptDetail(parseInt(selectedNode.id));
      if (conceptData) {
        // 设置表单初始值
        editForm.setFieldsValue({
          name: conceptData.name,
          description: conceptData.description || ''
        });
        
        setEditingConcept(conceptData);
        setEditConceptVisible(true);
        setNodeDetailVisible(false);
      }
    } catch (error) {
      console.error('准备编辑概念失败', error);
      message.error('获取概念详情失败');
    }
  };
  
  // 提交编辑概念
  const submitEditConcept = async (values: any) => {
    if (!editingConcept) return;
    
    // 保存当前视图状态
    if (graphRef.current) {
      const currentZoomLevel = graphRef.current.zoom();
      const currentCenterPos = graphRef.current.centerAt();
      
      setViewState({
        scale: currentZoomLevel,
        x: currentCenterPos?.x || 0,
        y: currentCenterPos?.y || 0
      });
    }
    
    try {
      await knowledgeGraphApi.updateConcept(editingConcept.id, values);
      message.success('概念更新成功');
      setEditConceptVisible(false);
      await fetchGraphData();  // 等待数据加载完成
    } catch (error) {
      console.error('更新概念失败', error);
      message.error('更新概念失败');
    }
  };
  
  // 处理删除概念
  const handleDeleteConcept = async () => {
    if (!selectedNode) return;
    
    // 保存当前视图状态
    if (graphRef.current) {
      const currentZoomLevel = graphRef.current.zoom();
      const currentCenterPos = graphRef.current.centerAt();
      
      setViewState({
        scale: currentZoomLevel,
        x: currentCenterPos?.x || 0,
        y: currentCenterPos?.y || 0
      });
    }
    
    try {
      await knowledgeGraphApi.deleteConcept(parseInt(selectedNode.id));
      message.success('概念已删除');
      setNodeDetailVisible(false);
      await fetchGraphData();  // 等待数据加载完成
    } catch (error) {
      console.error('删除概念失败', error);
      message.error('删除概念失败');
    }
  };

  // 修复renderLegend方法，使其适配深色背景
  const renderLegend = () => {
    return (
      <div style={{ 
        position: 'absolute', 
        bottom: 20, 
        left: 10, 
        zIndex: 10, 
        backgroundColor: 'rgba(30, 30, 30, 0.75)',
        padding: '12px',
        borderRadius: '4px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        maxWidth: '220px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <Typography.Title level={5} style={{ margin: 0, color: '#fff' }}>图例</Typography.Title>
          <Button 
            type="link" 
            size="small" 
            onClick={() => {
              setLegendModalVisible(true);
              // 防止自动缩放
            }} 
            style={{ padding: '0 5px', color: '#1890ff' }}
          >
            详细说明
          </Button>
        </div>
        <Typography.Text type="secondary" style={{ fontSize: '11px', color: '#bfbfbf' }}>
          点击节点查看详情，拖拽调整位置，滚轮缩放
        </Typography.Text>
      </div>
    );
  };

  // 修复设置面板，使其适配深色背景
  const renderConfigPanel = () => {
    return (
      <div style={{ 
        position: 'absolute', 
        top: 10, 
        right: 10, 
        zIndex: 10, 
        backgroundColor: 'rgba(30, 30, 30, 0.75)',
        padding: '12px',
        borderRadius: '4px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        width: '180px'
      }}>
        <Typography.Title level={5} style={{ margin: 0, marginBottom: '8px', color: '#fff' }}>图谱设置</Typography.Title>
        <div style={{ marginBottom: '12px' }}>
          <Typography.Text style={{ color: '#e8e8e8' }}>节点大小</Typography.Text>
          <Slider
            min={0.5}
            max={2}
            step={0.1}
            value={graphConfig.nodeSizeMultiplier}
            onChange={(val) => {
              setGraphConfig({...graphConfig, nodeSizeMultiplier: val});
              // 不再调用自动缩放函数
            }}
          />
        </div>
        <div>
          <Button 
            type="primary" 
            size="small" 
            onClick={() => {
              fetchGraphData();
              // 不再调用自动缩放函数
            }} 
            style={{ width: '100%' }}
          >
            刷新图谱
          </Button>
        </div>
      </div>
    );
  };

  // 修复图例详情模态框，确保正确显示
  const renderLegendModal = () => {
    return (
      <Modal
        title="知识图谱帮助说明"
        open={legendModalVisible}
        onCancel={() => {
          setLegendModalVisible(false);
          // 不再自动调整视图
        }}
        footer={[
          <Button key="close" onClick={() => {
            setLegendModalVisible(false);
            // 不再自动调整视图
          }}>
            关闭
          </Button>
        ]}
        width={700}
      >
        <div style={{ padding: '10px 0' }}>
          <Typography.Title level={4}>节点大小说明</Typography.Title>
          <div style={{ marginBottom: '20px' }}>
            <Typography.Paragraph>
              节点大小表示概念的重要性和关联的论文数量，节点越大代表该概念越重要或与更多论文相关联。
            </Typography.Paragraph>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
              <div style={{ width: '15px', height: '15px', borderRadius: '50%', backgroundColor: '#1890ff', marginRight: '10px' }}></div>
              <Typography.Text>较小节点：重要性较低或关联论文较少</Typography.Text>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
              <div style={{ width: '25px', height: '25px', borderRadius: '50%', backgroundColor: '#1890ff', marginRight: '10px' }}></div>
              <Typography.Text>中等节点：中等重要性或有一定数量关联论文</Typography.Text>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '35px', height: '35px', borderRadius: '50%', backgroundColor: '#1890ff', marginRight: '10px' }}></div>
              <Typography.Text>较大节点：核心概念或关联论文较多</Typography.Text>
            </div>
          </div>
          
          <Typography.Title level={4}>连接说明</Typography.Title>
          <div style={{ marginBottom: '20px' }}>
            <Typography.Paragraph>
              连接线表示概念之间的关系。连接线的粗细表示关系的强度，连接线上的箭头表示关系的方向。
            </Typography.Paragraph>
            <div style={{ marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                <div style={{ width: '40px', height: '2px', backgroundColor: '#666', marginRight: '10px' }}></div>
                <Typography.Text>细线：一般关联关系</Typography.Text>
              </div>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ width: '40px', height: '4px', backgroundColor: '#666', marginRight: '10px' }}></div>
                <Typography.Text>粗线：强关联关系</Typography.Text>
              </div>
            </div>
            <Typography.Paragraph>
              线上的粒子动画表示知识流动方向，从源概念流向目标概念。
            </Typography.Paragraph>
          </div>
          
          <Typography.Title level={4}>交互说明</Typography.Title>
          <div>
            <Typography.Paragraph>
              <ul>
                <li>点击节点：查看节点详情和相关论文</li>
                <li>拖拽节点：调整图谱布局</li>
                <li>滚轮缩放：放大缩小图谱</li>
                <li>拖拽空白处：平移图谱视图</li>
                <li>右上角控制面板：调整图谱参数</li>
                <li>右下角按钮：放大、缩小、适应屏幕</li>
              </ul>
            </Typography.Paragraph>
          </div>
        </div>
      </Modal>
    );
  };

  // 修改缩放控制面板样式
  const renderZoomControls = () => {
    return (
      <div style={{ 
        position: 'absolute', 
        bottom: 20, 
        right: 20,
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'rgba(30, 30, 30, 0.75)',
        borderRadius: '4px',
        padding: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
      }}>
        <Button 
          icon={<PlusOutlined style={{ color: '#fff' }} />} 
          size="small"
          type="text"
          onClick={() => {
            if (graphRef.current) {
              const currentZoom = graphRef.current.zoom();
              graphRef.current.zoom(currentZoom * 1.2, 400); // 缩放并动画过渡
            }
          }}
          style={{ marginBottom: '5px', color: '#fff' }}
        />
        <Button 
          icon={<MinusOutlined style={{ color: '#fff' }} />} 
          size="small"
          type="text"
          onClick={() => {
            if (graphRef.current) {
              const currentZoom = graphRef.current.zoom();
              graphRef.current.zoom(currentZoom / 1.2, 400);
            }
          }}
          style={{ marginBottom: '5px', color: '#fff' }}
        />
        <Button 
          icon={<FullscreenOutlined style={{ color: '#fff' }} />} 
          size="small"
          type="text"
          onClick={() => {
            if (graphRef.current) {
              graphRef.current.zoomToFit(400, 50); // 缩放以适合所有节点，带过渡动画
            }
          }}
          style={{ color: '#fff' }}
        />
      </div>
    );
  };
  
  // 简化zoomHandler逻辑
  const zoomHandler = useCallback(() => {
    try {
      // 不再需要更新迷你地图，只需记录当前的缩放状态
      if (graphRef.current) {
        setCurrentZoom(graphRef.current.zoom());
      }
    } catch (e) {
      console.error("缩放处理错误", e);
    }
  }, []);

  // 修改相关的useEffect钩子
  useEffect(() => {
    // 仅在组件挂载和graphRef变更时设置事件监听
    if (graphRef.current && graphRef.current._zoomBehavior) {
      try {
        // 添加缩放事件监听
        graphRef.current._zoomBehavior.on("zoom", zoomHandler);
      } catch (e) {
        console.error("添加缩放监听器失败", e);
      }
    }

    return () => {
      // 组件卸载时清理事件监听
      if (graphRef.current && graphRef.current._zoomBehavior) {
        try {
          graphRef.current._zoomBehavior.on("zoom", null);
        } catch (e) {
          console.error("移除缩放监听器失败", e);
        }
      }
    };
  }, [graphRef.current, zoomHandler]);

  // 更新节点详情模态框，使用外部状态变量
  const renderNodeDetailModal = () => {
    return (
      <Modal
        title={selectedNode ? `概念详情：${selectedNode.name}` : '概念详情'}
        open={nodeDetailVisible}
        onCancel={() => {
          setNodeDetailVisible(false);
          // 恢复之前保存的视图状态
          if (graphRef.current && viewState) {
            // 不再自动调整视图
          }
        }}
        footer={[
          <Button key="close" onClick={() => {
            setNodeDetailVisible(false);
            // 不再自动调整视图
          }}>关闭</Button>,
          <Button 
            key="edit" 
            type="primary" 
            onClick={handleEditConcept}
          >
            编辑
          </Button>,
          <Popconfirm
            title="确定要删除这个概念吗？"
            onConfirm={handleDeleteConcept}
            okText="确定"
            cancelText="取消"
          >
            <Button key="delete" danger>删除</Button>
          </Popconfirm>
        ]}
        width={600}
      >
        {selectedNode && (
          <div>
            <Descriptions bordered column={1} size="small" style={{ marginBottom: '20px' }}>
              <Descriptions.Item label="名称">{selectedNode.name}</Descriptions.Item>
              <Descriptions.Item label="描述">{selectedNode.description || '无描述'}</Descriptions.Item>
            </Descriptions>
            
            <Typography.Title level={5}>相关论文</Typography.Title>
            {selectedNodePapers && selectedNodePapers.length > 0 ? (
              <List
                size="small"
                dataSource={selectedNodePapers}
                renderItem={(paper: any) => (
                  <List.Item>
                    <List.Item.Meta
                      title={<a href={`/papers/${paper.id}`} target="_blank" rel="noopener noreferrer">{paper.title}</a>}
                      description={paper.authors}
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无相关论文" />
            )}
          </div>
        )}
      </Modal>
    );
  };

  // 定义学习路径渲染函数
  const renderReadingPathModal = () => {
    return (
      <Modal
        title="学习路径推荐"
        open={readingPathVisible}
        onCancel={() => setReadingPathVisible(false)}
        footer={null}
        width={700}
      >
        <Alert
          message="学习路径推荐"
          description="系统将分析您的知识图谱，为您推荐最佳的学习路径，帮助您更高效地掌握目标概念。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Form
          layout="vertical"
          onFinish={handleGetReadingPath}
        >
          <Form.Item
            label="目标概念"
            name="target_concept_id"
            rules={[{ required: true, message: '请选择一个目标概念' }]}
          >
            <Select
              placeholder="选择您想学习的目标概念"
              style={{ width: '100%' }}
              onChange={(value) => setSelectedConceptId(value)}
            >
              {Array.isArray(graphData?.nodes) && graphData.nodes.map((node: any) => (
                <Option key={node.id} value={node.id}>
                  {node.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loadingReadingPath}
              style={{ width: '100%' }}
            >
              生成学习路径
            </Button>
          </Form.Item>
        </Form>
        
        {readingPaths && readingPaths.length > 0 ? (
          <div>
            <Divider orientation="left">推荐学习路径</Divider>
            {readingPaths.map((path: ReadingPath, index: number) => (
              <div key={index} style={{ marginBottom: 16 }}>
                <Card 
                  title={`路径 ${index + 1}: ${path.path.length}个概念`}
                  size="small"
                >
                  <Timeline>
                    {path.path.map((concept: ReadingPathConcept, idx: number) => (
                      <Timeline.Item key={idx}>
                        <strong>{concept.name}</strong>
                        {concept.description && <p>{concept.description}</p>}
                        {concept.related_papers && concept.related_papers.length > 0 && (
                          <div>
                            <Text type="secondary">推荐阅读：</Text>
                            <ul style={{ paddingLeft: 20, marginTop: 4 }}>
                              {concept.related_papers.slice(0, 2).map((paper: {id: number, title: string, authors: string}) => (
                                <li key={paper.id}>
                                  <a onClick={() => window.open(`/paper/${paper.id}`, '_blank')}>
                                    {paper.title}
                                  </a>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </Timeline.Item>
                    ))}
                  </Timeline>
                </Card>
              </div>
            ))}
          </div>
        ) : loadingReadingPath ? (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <Spin tip="正在生成学习路径..." />
          </div>
        ) : null}
      </Modal>
    );
  };

  const navigate = useNavigate();

  return (
    <Layout style={{ height: '100vh', overflow: 'hidden' }}>
      <Content style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ marginBottom: '20px' }}>
          <Title level={2}>知识图谱</Title>
          <Paragraph>
            通过知识图谱可视化您的研究领域概念和关系，帮助您构建领域知识体系。
          </Paragraph>
        </div>
        
        <Row gutter={16} style={{ flex: 1, overflow: 'hidden' }}>
          <Col span={24} style={{ height: '100%' }}>
            <Card 
              title="知识网络" 
              style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              bodyStyle={{ flex: 1, padding: '12px', overflow: 'hidden' }}
              extra={
                <Space>
                  <Button type="primary" onClick={() => setAddConceptVisible(true)}>
                    添加概念
                  </Button>
                  <Button onClick={() => setAddRelationVisible(true)}>
                    添加关系
                  </Button>
                  <Dropdown menu={{
                    items: [
                      {
                        key: '1',
                        label: '论文相似度分析',
                        onClick: () => setCalculateSimilarityVisible(true)
                      },
                      {
                        key: '2',
                        label: '学习路径推荐',
                        onClick: () => setReadingPathVisible(true)
                      }
                    ]
                  }}>
                    <Button>
                      高级工具 <DownOutlined />
                    </Button>
                  </Dropdown>
                  <Button icon={<ReloadOutlined />} onClick={fetchGraphData}>
                    刷新
                  </Button>
                </Space>
              }
            >
              <div 
                ref={containerRef} 
                style={{ 
                  width: '100%', 
                  height: '100%', 
                  position: 'relative',
                  border: '1px solid #f0f0f0',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}
              >
                {loading && (
                  <div style={{ 
                    position: 'absolute', 
                    top: 0, 
                    left: 0, 
                    right: 0, 
                    bottom: 0, 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center',
                    background: 'rgba(255,255,255,0.7)',
                    zIndex: 5
                  }}>
                    <Spin size="large" tip="正在加载知识图谱..." />
                  </div>
                )}
                
                {renderConfigPanel()}
                {renderLegend()}
                {renderZoomControls()}
                {renderNodeDetailModal()}
                {renderLegendModal()}
                {renderReadingPathModal()}
                {/* 添加论文相似度计算模态框 */}
                <Modal
                  title="论文相似度分析"
                  open={calculateSimilarityVisible}
                  onCancel={() => setCalculateSimilarityVisible(false)}
                  footer={null}
                  width={800}
                >
                  <Form
                    layout="vertical"
                    onFinish={handleCalculateSimilarity}
                    initialValues={{ compareMode: 'all' }}
                  >
                    <Row gutter={[24, 16]}>
                      <Col span={24}>
                        <Form.Item
                          label="比较模式"
                          name="compareMode"
                        >
                          <Radio.Group 
                            onChange={(e) => setCompareMode(e.target.value as 'all' | 'specific')}
                            value={compareMode}
                            buttonStyle="solid"
                          >
                            <Radio.Button value="all">比较所有论文</Radio.Button>
                            <Radio.Button value="specific">比较特定论文</Radio.Button>
                          </Radio.Group>
                        </Form.Item>
                      </Col>
                      
                      <Col span={compareMode === 'specific' ? 12 : 24}>
                        <Form.Item
                          label="源论文"
                        >
                          <Select
                            style={{ width: '100%' }} 
                            placeholder="选择源论文"
                            value={simPaperId}
                            onChange={(value) => setSimPaperId(value)}
                          >
                            {userPapers.map(paper => (
                              <Option key={paper.id} value={paper.id}>
                                {paper.title.length > 30 ? paper.title.slice(0, 30) + '...' : paper.title}
                              </Option>
                            ))}
                          </Select>
                        </Form.Item>
                      </Col>
                      
                      {compareMode === 'specific' && (
                        <Col span={12}>
                          <Form.Item
                            label="目标论文"
                          >
                            <Select
                              style={{ width: '100%' }} 
                              placeholder="选择目标论文"
                              value={comparePaperId}
                              onChange={(value) => setComparePaperId(value)}
                            >
                              {userPapers.filter(p => p.id !== simPaperId).map(paper => (
                                <Option key={paper.id} value={paper.id}>
                                  {paper.title.length > 30 ? paper.title.slice(0, 30) + '...' : paper.title}
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                      )}
                      
                      {compareMode === 'all' && (
                        <Col span={18}>
                          <Form.Item
                            label="相似度阈值"
                          >
                            <Slider
                              min={0}
                              max={1}
                              step={0.05}
                              value={similarityThreshold}
                              onChange={(val) => setSimilarityThreshold(val)}
                              style={{ width: '100%' }}
                              marks={{ 0: '0', 0.5: '0.5', 1: '1' }}
                            />
                          </Form.Item>
                        </Col>
                      )}
                      
                      <Col span={compareMode === 'all' ? 6 : 24} style={{ textAlign: compareMode === 'all' ? 'right' : 'center' }}>
                        <Form.Item>
                          <Button 
                            type="primary" 
                            htmlType="submit"
                            loading={calculatingSimilarity}
                            size="middle"
                            style={{ padding: '0 24px', marginTop: compareMode === 'all' ? '30px' : '0' }}
                          >
                            计算相似度
                          </Button>
                        </Form.Item>
                      </Col>
                    </Row>
                  </Form>
                  
                  <Divider style={{ margin: '12px 0 24px 0' }} />

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
                        style={{ marginBottom: '16px' }}
                      />
                      
                      <Table
                        dataSource={similarPapers}
                        columns={similarPapersColumns}
                        rowKey="paper_id"
                        pagination={{ pageSize: 10 }}
                        size="small"
                      />
                    </>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                      {calculatingSimilarity ? (
                        <Spin tip="计算中..." size="large" />
                      ) : (
                        <Empty description="暂无相似论文数据" />
                      )}
                    </div>
                  )}

                  {/* 在模态框底部添加跳转链接 */}
                  <div style={{ marginTop: '24px', textAlign: 'center' }}>
                    <Divider style={{ margin: '8px 0 16px 0' }}>或者</Divider>
                    <Button type="link" onClick={() => {
                      setCalculateSimilarityVisible(false);
                      navigate('/paper-similarity');
                    }}>
                      前往专业论文相似度分析页面
                    </Button>
                  </div>
                </Modal>
                
                {/* 添加概念模态框 */}
                <Modal
                  title="添加概念"
                  open={addConceptVisible}
                  onCancel={() => setAddConceptVisible(false)}
                  footer={[
                    <Button key="cancel" onClick={() => setAddConceptVisible(false)}>
                      取消
                    </Button>,
                    <Button key="submit" type="primary" onClick={() => form.submit()}>
                      添加
                    </Button>
                  ]}
                >
                  <Form
                    form={form}
                    onFinish={handleAddConcept}
                    layout="vertical"
                  >
                    <Form.Item
                      name="name"
                      label="概念名称"
                      rules={[{ required: true, message: '请输入概念名称' }]}
                    >
                      <Input placeholder="输入概念名称" />
                    </Form.Item>
                    
                    <Form.Item
                      name="description"
                      label="概念描述"
                    >
                      <Input.TextArea 
                        placeholder="输入概念描述" 
                        rows={4}
                      />
                    </Form.Item>
                  </Form>
                </Modal>
                
                {/* 添加关系模态框 */}
                <Modal
                  title="添加关系"
                  open={addRelationVisible}
                  onCancel={() => setAddRelationVisible(false)}
                  footer={[
                    <Button key="cancel" onClick={() => setAddRelationVisible(false)}>
                      取消
                    </Button>,
                    <Button key="submit" type="primary" onClick={() => relationForm.submit()}>
                      添加
                    </Button>
                  ]}
                >
                  <Form
                    form={relationForm}
                    onFinish={handleAddRelation}
                    layout="vertical"
                  >
                    <Form.Item
                      name="source"
                      label="源概念"
                      rules={[{ required: true, message: '请选择源概念' }]}
                    >
                      <Select
                        placeholder="选择源概念"
                        showSearch
                        optionFilterProp="children"
                      >
                        {concepts.map(concept => (
                          <Option key={concept.id} value={concept.id}>
                            {concept.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    
                    <Form.Item
                      name="relation_type"
                      label="关系类型"
                      initialValue="关联"
                    >
                      <Select>
                        <Option value="关联">关联</Option>
                        <Option value="部分">部分</Option>
                        <Option value="应用">应用</Option>
                        <Option value="依赖">依赖</Option>
                        <Option value="扩展">扩展</Option>
                      </Select>
                    </Form.Item>
                    
                    <Form.Item
                      name="target"
                      label="目标概念"
                      rules={[{ required: true, message: '请选择目标概念' }]}
                    >
                      <Select
                        placeholder="选择目标概念"
                        showSearch
                        optionFilterProp="children"
                      >
                        {concepts.map(concept => (
                          <Option key={concept.id} value={concept.id}>
                            {concept.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Form>
                </Modal>
                
                {/* 从论文提取概念模态框 */}
                <Modal
                  title="从论文提取概念"
                  open={extractConceptsVisible}
                  onCancel={() => setExtractConceptsVisible(false)}
                  footer={[
                    <Button key="cancel" onClick={() => setExtractConceptsVisible(false)}>
                      取消
                    </Button>,
                    <Button 
                      key="submit" 
                      type="primary" 
                      onClick={handleExtractConcepts}
                      loading={extractingConcepts}
                    >
                      提取概念
                    </Button>
                  ]}
                >
                  <Alert
                    message="功能说明"
                    description="系统将从选择的论文中提取关键概念，并自动将它们添加到知识图谱中。同时会尝试建立概念之间的关系。"
                    type="info"
                    showIcon
                    style={{ marginBottom: '16px' }}
                  />
                  
                  <Form
                    form={extractForm}
                    layout="vertical"
                  >
                    <Form.Item
                      name="paper_id"
                      label="选择论文"
                      rules={[{ required: true, message: '请选择一篇论文' }]}
                    >
                      <Select
                        placeholder="选择要提取概念的论文"
                        showSearch
                        optionFilterProp="children"
                        value={selectedPaperId}
                        onChange={(value) => setSelectedPaperId(value)}
                      >
                        {userPapers.map(paper => (
                          <Option key={paper.id} value={paper.id}>
                            {paper.title}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Form>
                  
                  <Divider />
                  
                  <Button 
                    type="default" 
                    block 
                    onClick={handleBatchExtractConcepts}
                  >
                    批量处理全部论文
                  </Button>
                </Modal>
                
                {/* 添加其他需要的编辑模态框 */}
                <Modal
                  title="编辑概念"
                  open={editConceptVisible}
                  onCancel={() => setEditConceptVisible(false)}
                  footer={[
                    <Button key="cancel" onClick={() => setEditConceptVisible(false)}>
                      取消
                    </Button>,
                    <Button key="submit" type="primary" onClick={() => editForm.submit()}>
                      保存
                    </Button>
                  ]}
                >
                  <Form
                    form={editForm}
                    onFinish={submitEditConcept}
                    layout="vertical"
                  >
                    <Form.Item
                      name="name"
                      label="概念名称"
                      rules={[{ required: true, message: '请输入概念名称' }]}
                    >
                      <Input />
                    </Form.Item>
                    <Form.Item
                      name="description"
                      label="概念描述"
                    >
                      <Input.TextArea rows={4} />
                    </Form.Item>
                  </Form>
                </Modal>

                {graphData && Array.isArray(graphData.nodes) && graphData.nodes.length > 0 ? (
                  <ForceGraph2D
                    ref={graphRef}
                    graphData={{
                      nodes: Array.isArray(graphData.nodes) ? graphData.nodes : [],
                      links: Array.isArray(graphData.links) ? graphData.links : []
                    } as ForceGraphData}
                    nodeLabel={(node: any) => `${node.name}: ${node.description || '无描述'}`}
                    linkLabel={(link: any) => `${link.value || '关系'}`}
                    nodeColor={(node: any) => {
                      // 如果节点被高亮显示，返回高亮颜色
                      if (highlightedNodes.has(node.id)) {
                        return '#ff5500';
                      }
                      
                      // 所有节点统一使用蓝色
                      return '#1890ff';
                    }}
                    nodeVal={(node: any) => {
                      // 基础大小乘以配置的倍数
                      const baseSize = Math.max(4, Math.min(12, 6 + (node.paperCount || 0) / 2));
                      return baseSize * graphConfig.nodeSizeMultiplier;
                    }}
                    linkWidth={(link: any) => 1.5 * (link.weight || 1)}
                    linkCurvature={(link: any) => link.curvature || 0}
                    d3AlphaDecay={0.02}
                    d3VelocityDecay={0.4}
                    d3AlphaMin={0.001}
                    enableNodeDrag={true}
                    enableZoomInteraction={true}
                    enablePanInteraction={true}
                    width={width}
                    height={height}
                    onNodeClick={handleNodeClick}
                    onNodeHover={(node: any) => {
                      // 如果已经有一个悬停节点，直接用null替换
                      if (!node) {
                        return;
                      }
                      // 否则手动处理悬停状态
                      const current = document.getElementById(`node-${node.id}`);
                      if (current) {
                        current.style.cursor = 'pointer';
                      }
                    }}
                    nodeCanvasObjectMode={() => "after"}
                    nodeCanvasObject={(node: any, ctx: any, globalScale: number) => {
                      // 绘制节点标签
                      const label = node.name;
                      const fontSize = 12 / globalScale;
                      ctx.font = `${fontSize}px Arial`;
                      const textWidth = ctx.measureText(label).width;
                      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4);
                      
                      // 当缩放比例足够大时才显示标签
                      if (globalScale >= 0.6) {
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                        ctx.fillRect(
                          node.x - bckgDimensions[0] / 2,
                          node.y + fontSize * 0.8,
                          bckgDimensions[0],
                          bckgDimensions[1]
                        );
                        
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = '#222';
                        ctx.fillText(
                          label,
                          node.x,
                          node.y + fontSize * 1.5
                        );
                      }
                    }}
                  />
                ) : (
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center', 
                    height: '100%',
                    flexDirection: 'column' 
                  }}>
                    <Text style={{ marginBottom: '16px' }}>
                      知识图谱为空。您可以手动添加概念和关系，或从已有论文中自动提取概念构建图谱。
                    </Text>
                    <Space>
                      <Button type="primary" onClick={() => setAddConceptVisible(true)}>
                        添加第一个概念
                      </Button>
                      <Button onClick={() => setExtractConceptsVisible(true)}>
                        从论文提取概念
                      </Button>
                    </Space>
                  </div>
                )}
              </div>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default KnowledgeGraph as React.ComponentType; 