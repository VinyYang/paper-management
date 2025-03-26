import React, { useState, useEffect, useRef } from 'react';
import { 
  Input, Button, Card, Typography, message, Space, Tooltip, 
  Tag, Form, Modal, Dropdown, Menu, Divider, theme, Row, Col, Drawer, Select, Badge, Empty,
  Table, Spin, Tabs
} from 'antd';
import { 
  SearchOutlined, CopyOutlined, UserOutlined,
  InfoCircleOutlined, ClockCircleOutlined, DeleteOutlined,
  HistoryOutlined, LoadingOutlined, FileTextOutlined,
  DownloadOutlined, GlobalOutlined, LinkOutlined, BookOutlined,
  CalendarOutlined, TeamOutlined, FilePdfOutlined, TrophyOutlined,
  QuestionCircleOutlined, DownOutlined, WarningOutlined
} from '@ant-design/icons';
import { searchApi, paperApi, projectApi, errorManager, scihubApi } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useSettings } from '../contexts/SettingsContext';
import { SearchResult } from '../services/api/searchApi';
import { publicationRankApi, rankColors, RankResult } from '../services/api/publicationRankApi';

const { Title, Paragraph, Text } = Typography;
const { useToken } = theme;
const { Option } = Select;
const { TabPane } = Tabs;

interface SearchHistory {
  keyword: string;
  author: string;
  timestamp: number;
}

interface Project {
  id: number;
  name: string;
}

// 添加自定义扩展接口以包含期刊等级信息
interface EnhancedSearchResult extends SearchResult {
  journalRanks?: RankResult[];
}

// 添加帮助信息弹窗
const HelpInfoModal: React.FC<{
  visible: boolean;
  onClose: () => void;
}> = ({ visible, onClose }) => {
  return (
    <Modal
      title="Sci-Hub访问帮助"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>
      ]}
      width={600}
    >
      <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
        <h3>为什么无法自动获取论文？</h3>
        <Paragraph>
          由于浏览器的安全限制(CORS政策)和网络环境的限制，从浏览器直接访问Sci-Hub可能会失败。
          这是一个常见问题，并非软件本身的缺陷。
        </Paragraph>
        
        <h3>如何解决？</h3>
        <ol>
          <li>
            <strong>直接访问链接</strong> - 点击搜索结果中的"直接访问"按钮，在新标签页中打开Sci-Hub。
          </li>
          <li>
            <strong>换用浏览器</strong> - Firefox、Edge或Safari可能比Chrome更容易访问Sci-Hub。
          </li>
          <li>
            <strong>处理安全警告</strong> - 如果浏览器显示"不安全连接"，点击"高级"然后"继续前往网站"。
          </li>
          <li>
            <strong>换用网络</strong> - 如果您在学校或公司网络，可能需要使用家庭网络或移动网络。
          </li>
          <li>
            <strong>尝试不同镜像站</strong> - Sci-Hub有多个镜像站，尝试搜索结果中提供的所有链接。
          </li>
        </ol>
        
        <h3>Sci-Hub使用提示</h3>
        <ul>
          <li>Sci-Hub主要通过DOI号查找论文，使用DOI搜索成功率最高。</li>
          <li>DOI号格式通常类似：10.1038/s41586-021-03724-8</li>
          <li>如果您有论文标题，建议先搜索Google Scholar找到DOI，再使用DOI搜索Sci-Hub。</li>
          <li>Sci-Hub可能无法获取最新(2年内)发表的论文。</li>
        </ul>
      </div>
    </Modal>
  );
};

const ScihubSearch: React.FC = () => {
  const [searchText, setSearchText] = useState<string>('');
  const [authorText, setAuthorText] = useState<string>('');
  const [results, setResults] = useState<EnhancedSearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [messageApi, contextHolder] = message.useMessage();
  const { language, themeMode } = useSettings();
  const [form] = Form.useForm();
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [isHistoryModalVisible, setIsHistoryModalVisible] = useState<boolean>(false);
  const [modalData, setModalData] = useState<SearchResult | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>([]);
  const [selectedHistory, setSelectedHistory] = useState<SearchHistory | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const [isHistoryDrawerVisible, setIsHistoryDrawerVisible] = useState<boolean>(false);
  const { token } = useToken();
  const [journalName, setJournalName] = useState<string>('');
  const [journalRanks, setJournalRanks] = useState<RankResult[]>([]);
  const [rankLoading, setRankLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('search');
  const [helpModalVisible, setHelpModalVisible] = useState<boolean>(false);
  
  // 是否深色模式
  const isDarkMode = themeMode === 'dark' || (themeMode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  // 获取搜索历史
  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        setSearchHistory(parsed);
      } catch (e) {
        console.error('Failed to parse search history', e);
      }
    }
  }, []);

  // 保存搜索历史
  const saveSearchHistory = (history: SearchHistory[]) => {
    localStorage.setItem('searchHistory', JSON.stringify(history));
  };

  // 格式化时间戳
  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // 应用历史搜索
  const applyHistorySearch = (history: SearchHistory) => {
    setSearchText(history.keyword);
    setAuthorText(history.author);
    setIsHistoryModalVisible(false);
    setIsHistoryDrawerVisible(false);
    handleSearch(history.keyword, history.author);
  };

  // 打开历史记录模态框
  const openHistoryModal = (history: SearchHistory) => {
    setSelectedHistory(history);
    setIsHistoryModalVisible(true);
  };

  // 清除搜索历史
  const clearSearchHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('searchHistory');
    setIsHistoryDrawerVisible(false);
  };

  // 翻译函数
  const getTranslation = (zhText: string, enText: string) => {
    return language === 'zh_CN' ? zhText : enText;
  };

  // 检测输入是否为DOI
  const isDOI = (text: string): boolean => {
    const doiPattern = /\b(10\.\d{4,}(?:\.\d+)*\/(?:(?!["&\'<>])\S)+)\b/i;
    const result = doiPattern.test(text);
    console.log(`检测DOI: "${text}" 结果: ${result}`);
    return result;
  };

  // 处理搜索
  const handleSearch = async (keyword?: string, author?: string) => {
    const searchKeyword = keyword || searchText;
    const searchAuthor = author || authorText;
    
    if (!searchKeyword.trim() && !searchAuthor.trim()) {
      messageApi.warning(getTranslation('请输入搜索内容', 'Please enter search text'));
      return;
    }

    setLoading(true);
    setResults([]);

    // 添加到搜索历史
    if (searchKeyword.trim() || searchAuthor.trim()) {
      const newHistory = {
        keyword: searchKeyword.trim(),
        author: searchAuthor.trim(),
        timestamp: Date.now()
      };
      
      // 避免重复添加相同的搜索
      const exists = searchHistory.some(
        item => item.keyword === newHistory.keyword && item.author === newHistory.author
      );
      
      if (!exists) {
        const updatedHistory = [newHistory, ...searchHistory].slice(0, 10); // 保留最近的10条记录
        setSearchHistory(updatedHistory);
        saveSearchHistory(updatedHistory);
      }
    }

    try {
      let response: {data: SearchResult[]} = {data: []};
      
      // 首先检查是否为DOI
      if (isDOI(searchKeyword)) {
        console.log('使用searchDOI搜索DOI');
        try {
          // 先尝试直接从Sci-Hub获取
          response = await searchApi.searchDOI(searchKeyword);
      } catch (error) {
          console.error('直接从Sci-Hub获取失败，尝试使用备用方法:', error);
          messageApi.info(getTranslation('正在尝试备用搜索方法...', 'Trying alternative search methods...'));
          
          // 如果第一种方法失败，尝试使用链接列表
          const sciHubUrls = scihubApi.getDirectLinks(searchKeyword);
          messageApi.info(
            getTranslation(
              '您可以尝试从以下链接手动访问: ', 
              'You can try manually accessing from these links: '
            ) + sciHubUrls.join(', ')
          );
          
          // 返回一个基本结果
          response = {
            data: [{
              id: Math.floor(Math.random() * 1000000),
              title: `论文: ${searchKeyword}`,
              authors: [getTranslation('未找到作者信息', 'No author information')],
              year: new Date().getFullYear(),
              journal: getTranslation('未找到期刊信息', 'No journal information'),
              abstract: getTranslation('由于浏览器安全限制，无法直接获取论文信息。请尝试从以下链接手动访问:', 'Due to browser security restrictions, paper information cannot be directly retrieved. Please try manually accessing from the following links:') + 
                       '\n' + sciHubUrls.join('\n'),
              doi: searchKeyword,
              url: `https://doi.org/${searchKeyword}`,
              source: 'scihub',
              has_pdf: false
            }]
          };
      }
    } else {
        // 非DOI搜索
        if (searchAuthor.trim()) {
          console.log('使用searchScihub搜索标题+作者');
          try {
            response = await searchApi.searchScihub(searchKeyword, searchAuthor);
          } catch (error) {
            console.error('从Sci-Hub搜索失败，尝试使用谷歌学术:', error);
            messageApi.info(getTranslation('从Sci-Hub搜索失败，尝试使用谷歌学术...', 'Failed to search from Sci-Hub, trying Google Scholar...'));
            response = await searchApi.searchScholar(searchKeyword + ' ' + searchAuthor);
          }
        } else {
          console.log('使用searchScholar搜索标题');
          try {
            response = await searchApi.searchScholar(searchKeyword);
          } catch (error) {
            console.error('从谷歌学术搜索失败:', error);
            messageApi.error(getTranslation('搜索失败', 'Search failed'));
            // 返回一个错误提示
            response = {
              data: [{
                id: Math.floor(Math.random() * 1000000),
                title: getTranslation('搜索失败', 'Search failed'),
                authors: [getTranslation('系统提示', 'System message')],
                year: new Date().getFullYear(),
                journal: '',
                abstract: getTranslation(
                  '由于浏览器安全限制，无法直接从谷歌学术获取数据。您可以尝试手动访问谷歌学术镜像站: ', 
                  'Due to browser security restrictions, data cannot be retrieved directly from Google Scholar. You can try manually accessing Google Scholar mirrors: '
                ) + searchApi.scholarMirrors.join(', '),
                doi: '',
                url: '',
                source: 'scholar',
                has_pdf: false
              }]
            };
          }
        }
      }

      if (response && response.data && response.data.length > 0) {
        // 确保所有结果都有authors数组
        const safeResults = response.data.map(result => ({
          ...result,
          authors: Array.isArray(result.authors) ? result.authors : [],
          journalRanks: [] as RankResult[] // 添加journalRanks属性
        }));
        setResults(safeResults);
        
        // 为每个有期刊名的结果查询期刊等级
        const resultsWithRankPromises = safeResults.map(async (result, index) => {
          if (result.journal && result.journal.trim()) {
            try {
              const rankResults = await publicationRankApi.getPublicationRank(result.journal);
              return {
                ...result,
                journalRanks: rankResults
              };
      } catch (error) {
              console.error(`获取期刊"${result.journal}"等级失败:`, error);
              return result;
            }
          }
          return result;
        });
        
        // 等待所有期刊等级查询完成
        const resultsWithRanks = await Promise.all(resultsWithRankPromises);
        setResults(resultsWithRanks);
        
        // 仍然查询第一个期刊填充期刊等级标签页
        for (const result of safeResults) {
          if (result.journal && result.journal.trim()) {
            setJournalName(result.journal);
            const rankResults = await publicationRankApi.getPublicationRank(result.journal);
            setJournalRanks(rankResults);
            break;
          }
        }
      } else {
        setResults([]);
        messageApi.info(getTranslation('未找到相关文献', 'No relevant papers found'));
      }
    } catch (error) {
      console.error('搜索出错:', error);
      errorManager.handleError(error, getTranslation('搜索失败', 'Search failed'));
      setResults([]);
      
      // 显示友好的错误信息和建议
      messageApi.error(
        getTranslation(
          '由于浏览器安全限制，可能无法直接获取搜索结果。您可以尝试从以下网站手动搜索:',
          'Due to browser security restrictions, search results may not be directly accessible. You can try searching manually from these websites:'
        )
      );
      
      // 显示可用的镜像站链接
      if (isDOI(searchKeyword)) {
        const sciHubUrls = scihubApi.scihubMirrors.map((mirror: string) => `${mirror}/${searchKeyword}`);
        messageApi.info(
          getTranslation('Sci-Hub镜像站: ', 'Sci-Hub mirrors: ') + 
          sciHubUrls.join(', ')
        );
      } else {
        messageApi.info(
          getTranslation('谷歌学术镜像站: ', 'Google Scholar mirrors: ') + 
          searchApi.scholarMirrors.join(', ')
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // 复制DOI
  const handleCopyDoi = (doi: string | undefined) => {
    if (!doi) {
      messageApi.warning(getTranslation('无DOI信息可复制', 'No DOI information to copy'));
      return;
    }
    navigator.clipboard.writeText(doi)
      .then(() => messageApi.success(getTranslation('DOI已复制', 'DOI copied')))
      .catch(() => messageApi.error(getTranslation('复制失败', 'Copy failed')));
  };

  // 在Sci-Hub中打开
  const handleOpenScihub = (doi: string | undefined) => {
    if (!doi) {
      messageApi.info(getTranslation('此结果没有DOI信息', 'This result has no DOI information'));
      return;
    }
    
    const links = scihubApi.getDirectLinks(doi);
    
    // 打开第一个链接
    window.open(links[0], '_blank');
    messageApi.info(getTranslation('在新窗口打开Sci-Hub', 'Opening Sci-Hub in a new window'));
  };

  // 显示Sci-Hub镜像站链接下拉菜单
  const renderScihubDropdown = (doi: string | undefined) => {
    if (!doi) return null;
    
    const links = scihubApi.getDirectLinks(doi);
    
    return (
      <Dropdown 
        menu={{ 
          items: [
            ...links.map((link, index) => ({
              key: `link-${index}`,
              label: (
                <a href={link} target="_blank" rel="noopener noreferrer">
                  {`${getTranslation('镜像站', 'Mirror')} ${index + 1}: ${link.split('/')[2]}`}
                </a>
              )
            })),
            {
              key: 'original-doi',
              label: (
                <a href={`https://doi.org/${doi}`} target="_blank" rel="noopener noreferrer">
                  {getTranslation('原始DOI链接', 'Original DOI Link')}
                </a>
              )
            }
          ]
        }} 
        placement="bottomRight"
      >
        <Button type="primary" style={{ marginLeft: 8 }}>
          {getTranslation('更多链接', 'More Links')} <DownOutlined />
        </Button>
      </Dropdown>
    );
  };

  // 下载论文
  const handleDownloadPaper = (doi: string) => {
    // 获取Sci-Hub直接链接
    const links = scihubApi.getDirectLinks(doi);
    // 打开第一个链接
    window.open(links[0], '_blank');
    messageApi.info(getTranslation('在新窗口打开Sci-Hub', 'Opening Sci-Hub in a new window'));
  };

  // 谷歌学术搜索
  const handleGoogleScholar = (title: string) => {
    const scholarUrl = `${searchApi.scholarMirrors[0]}/scholar?q=${encodeURIComponent(title)}`;
    window.open(scholarUrl, '_blank');
    messageApi.info(getTranslation('在新窗口打开谷歌学术', 'Opening Google Scholar in a new window'));
  };

  // 获取项目列表
  const fetchProjects = async () => {
    try {
      setProjectsLoading(true);
      const response = await projectApi.getProjects();
      const projectData = Array.isArray(response) ? response : (
        Array.isArray(response.data) ? response.data : [response.data]
      );
      setProjects(projectData.filter(Boolean));
      return projectData.filter(Boolean); // 返回过滤后的项目数据
    } catch (error) {
      console.error('获取项目列表失败', error);
      errorManager.handleError(error, getTranslation('获取项目列表失败', 'Failed to fetch projects'));
      return []; // 出错时返回空数组
    } finally {
      setProjectsLoading(false);
    }
  };

  // 添加期刊等级说明信息
  const renderRankLegend = () => {
    if (results.length === 0 || !results.some(r => r.journalRanks && r.journalRanks.length > 0)) {
      return null;
    }

    return (
      <div style={{ 
        marginTop: 16, 
        padding: '12px', 
        background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillTertiary),
        borderRadius: token.borderRadiusSM,
        fontSize: '13px'
      }}>
        <Text type="secondary" strong>
          <InfoCircleOutlined style={{ marginRight: 8 }} />
          {getTranslation('期刊等级说明', 'Journal Ranking Guide')}
        </Text>
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: '8px', 
          marginTop: 8,
          alignItems: 'center' 
        }}>
          <Tag style={{ 
            backgroundColor: rankColors[1], 
            color: rankColors.textColor, 
            fontSize: rankColors.fontSize,
            fontWeight: 'bold',
            padding: '0px 4px',
          }}>
            {getTranslation('顶级期刊', 'Top Journal')}
          </Tag>
          <Tag style={{ 
            backgroundColor: rankColors[2], 
            color: rankColors.textColor, 
            fontSize: rankColors.fontSize,
            fontWeight: 'bold',
            padding: '0px 4px',
          }}>
            {getTranslation('重要期刊', 'Important Journal')}
          </Tag>
          <Tag style={{ 
            backgroundColor: rankColors[3], 
            color: rankColors.textColor, 
            fontSize: rankColors.fontSize,
            fontWeight: 'bold',
            padding: '0px 4px',
          }}>
            {getTranslation('一般期刊', 'General Journal')}
          </Tag>
          <Text type="secondary" style={{ fontSize: '12px', marginLeft: 8 }}>
            {getTranslation('颜色标签表示期刊等级，可用于评估文献质量', 'Color tags indicate journal ranking, useful for evaluating literature quality')}
          </Text>
        </div>
      </div>
    );
  };

  // 添加到文献库
  const handleAddToLibrary = (record: EnhancedSearchResult) => {
    // 首先获取项目列表，这样可以在表单初始化前获取项目数据
    fetchProjects().then(() => {
      // 获取URL中的项目ID参数
      const urlParams = new URLSearchParams(window.location.search);
      const projectIdFromUrl = urlParams.get('project_id');
      
      // 设置表单默认值
      form.setFieldsValue({
        title: record.title,
        authors: Array.isArray(record.authors) ? record.authors.join(', ') : record.authors,
        journal: record.journal,
        year: record.year,
        doi: record.doi,
        abstract: record.abstract,
        // 如果URL中有项目ID参数则使用，否则使用第一个可用项目
        project_id: projectIdFromUrl || (projects.length > 0 ? projects[0].id : undefined)
      });
      
      setModalData(record);
      setIsModalVisible(true);
    });
    
    // 如果有期刊等级信息，保存到localStorage以便详情页使用
    if (record.journal && record.journalRanks && record.journalRanks.length > 0) {
      try {
        localStorage.setItem(`journal_rank_${record.journal}`, JSON.stringify(record.journalRanks));
      } catch (e) {
        console.error('保存期刊等级信息失败', e);
      }
    }
  };

  // 提交添加文献表单
  const handleSubmit = async (values: any) => {
    try {
      // 创建论文对象时就包含 project_id
      const paperResponse = await paperApi.createPaper({
        title: values.title,
        authors: values.authors,
        journal: values.journal,
        year: values.year,
        doi: values.doi,
        abstract: values.abstract,
        project_id: values.project_id || null  // 确保包含 project_id
      });

      // 如果选择了项目并成功创建了论文，则关联论文到项目
      if (values.project_id && paperResponse && paperResponse.data && paperResponse.data.id) {
        await projectApi.addPaper(values.project_id, paperResponse.data.id);
        messageApi.success(getTranslation(
          '论文已添加到文献库并关联到项目', 
          'Paper added to library and linked to project'
        ));
      } else {
        messageApi.success(getTranslation('论文已添加到文献库', 'Paper added to library'));
      }
      
      setIsModalVisible(false);
      form.resetFields();
    } catch (error) {
      errorManager.handleError(error, getTranslation('添加论文失败', 'Failed to add paper'));
    }
  };

  // 获取不同主题下的样式
  const getThemedStyle = (light: any, dark: any) => {
    return isDarkMode ? dark : light;
  };

  // 查询期刊等级
  const handleJournalRankSearch = async (journalNameParam?: string | React.KeyboardEvent<HTMLInputElement> | React.MouseEvent<HTMLElement, MouseEvent>) => {
    // 处理不同类型的参数
    let journalNameToSearch = journalName;
    
    // 如果参数是字符串，直接使用
    if (typeof journalNameParam === 'string') {
      journalNameToSearch = journalNameParam;
    }
    // 其他情况下使用state中的journalName
    
    if (!journalNameToSearch.trim()) {
      messageApi.warning(getTranslation('请输入期刊名称', 'Please enter journal name'));
      return;
    }

    setRankLoading(true);
    setJournalRanks([]);

    try {
      const results = await publicationRankApi.getPublicationRank(journalNameToSearch);
      setJournalRanks(results);
      
      if (results.length === 0) {
        messageApi.info(getTranslation('未找到相关期刊等级信息', 'No journal ranking information found'));
      } else {
        messageApi.success(
          getTranslation(
            `成功获取期刊"${journalNameToSearch}"的分级信息`, 
            `Successfully fetched ranking information for journal "${journalNameToSearch}"`
          )
        );
      }
    } catch (error) {
      console.error('期刊等级查询失败:', error);
      errorManager.handleError(error, getTranslation('期刊等级查询失败', 'Failed to fetch journal ranking'));
    } finally {
      setRankLoading(false);
    }
  };

  // 获取等级颜色
  const getRankColor = (result: RankResult) => {
    if (result.type === 'custom' && result.level !== undefined) {
      return rankColors[result.level];
    }
    return undefined;
  };

  // 渲染期刊等级查询结果
  const renderJournalRanks = () => {
    const columns = [
      {
        title: getTranslation('数据来源', 'Source'),
        dataIndex: 'source',
        key: 'source',
        render: (text: string) => <Text strong>{text.toUpperCase()}</Text>
      },
      {
        title: getTranslation('等级', 'Rank'),
        dataIndex: 'rank',
        key: 'rank',
        render: (text: string, record: RankResult) => (
          <Tag
            style={{
              backgroundColor: getRankColor(record),
              color: rankColors.textColor,
              fontSize: rankColors.fontSize,
              fontWeight: 'bold',
              padding: '2px 8px',
              borderRadius: '4px'
            }}
          >
            {text}
          </Tag>
        )
      }
    ];
    
    return (
      <div>
        {rankLoading ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 0', 
            background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillSecondary),
            borderRadius: token.borderRadiusLG
          }}>
            <Spin size="large" />
            <div style={{ marginTop: 16, color: token.colorTextSecondary }}>
              {getTranslation('查询中...', 'Searching...')}
            </div>
          </div>
        ) : journalRanks.length > 0 ? (
          <Table 
            dataSource={journalRanks}
            columns={columns} 
            rowKey={(record) => `${record.source}-${record.rank}`}
            pagination={false}
            bordered
            size="middle"
            style={{
              borderRadius: token.borderRadiusLG,
              overflow: 'hidden'
            }}
          />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={getTranslation('暂无数据', 'No Data')}
            style={{ 
              padding: '40px 0', 
              background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillSecondary),
              borderRadius: token.borderRadiusLG
            }}
          />
        )}
      </div>
    );
  };

  // 渲染期刊级别标签
  const renderJournalRankBadges = (result: EnhancedSearchResult) => {
    if (!result.journalRanks || result.journalRanks.length === 0) {
      return null;
    }
    
    // 对期刊等级进行排序：官方等级优先，然后按等级排序
    const sortedRanks = [...result.journalRanks].sort((a, b) => {
      // 官方等级优先
      if (a.type === 'official' && b.type !== 'official') return -1;
      if (a.type !== 'official' && b.type === 'official') return 1;
      
      // 然后按等级排序
      const levelA = a.level || 3;
      const levelB = b.level || 3;
      return levelA - levelB;
    });
    
    // 直接显示所有等级标签，不使用下拉菜单
    return (
      <div style={{ 
        display: 'flex', 
        marginTop: 8,
        alignItems: 'center', 
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        {sortedRanks.map((rank, idx) => {
          // 确定等级颜色
          let rankLevel = rank.level || 3;
          if (rank.type === 'official') {
            if (rank.rank.includes('CCF-A')) rankLevel = 1;
            else if (rank.rank.includes('CCF-B')) rankLevel = 2; 
            else if (rank.rank.includes('CCF-C')) rankLevel = 3;
            else if (rank.rank.includes('CSSCI')) rankLevel = 2;
            else if (rank.rank.includes('SCI')) rankLevel = 1;
            else if (rank.rank.includes('EI')) rankLevel = 2;
          }
          
          return (
            <Tag
              key={`${idx}-${rank.source}-${rank.rank}`}
              style={{
                backgroundColor: rankColors[rankLevel],
                color: rankColors.textColor,
                fontSize: rankColors.fontSize,
                fontWeight: 'bold',
                padding: '2px 8px',
                borderRadius: '4px',
                margin: 0,
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
            >
              {rank.rank}
            </Tag>
          );
        })}
      </div>
    );
  };

  // 渲染搜索失败时的帮助卡片
  const renderFailureCard = (result: EnhancedSearchResult) => {
    const isDoi = result.doi && result.doi.match(/10\.\d{4,}[\d\.]+\/[^&\s#]+/);

    return (
        <Card
        style={{ 
          marginBottom: 16,
          borderColor: token.colorErrorBorder,
          backgroundColor: getThemedStyle(
            'rgba(255, 77, 79, 0.05)',
            'rgba(255, 77, 79, 0.1)'
          )
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <Title level={5} style={{ color: token.colorError, marginTop: 0 }}>
              <WarningOutlined /> {result.title}
            </Title>
            <Paragraph>{result.abstract}</Paragraph>
            
            {/* 论文信息 */}
            {isDoi && (
              <Space direction="vertical" size="small" style={{ width: '100%', marginBottom: 16 }}>
                <div>
                  <Text type="secondary"><LinkOutlined /> DOI: </Text>
                  <Text 
                    copyable={{
                      text: result.doi,
                      onCopy: () => messageApi.success(getTranslation('DOI已复制', 'DOI copied'))
                    }}
                  >
                    {result.doi}
                  </Text>
                </div>
                {result.journal && (
                  <div>
                    <Text type="secondary"><BookOutlined /> 期刊: </Text>
                    <Text strong style={{ color: token.colorPrimary }}>{result.journal}</Text>
                  </div>
                )}
              </Space>
            )}
            
            {isDoi && (
              <div style={{ marginTop: 16 }}>
                <Space>
                  <Button 
                    type="primary" 
                    icon={<GlobalOutlined />} 
                    onClick={() => handleOpenScihub(result.doi)}
                  >
                    {getTranslation('直接访问', 'Direct Access')}
                  </Button>
                  {renderScihubDropdown(result.doi)}
                  <Button 
                    icon={<CopyOutlined />}
                    onClick={() => handleCopyDoi(result.doi)}
                  >
                    {getTranslation('复制DOI', 'Copy DOI')}
                  </Button>
                  <Button 
                    type="default" 
                    onClick={() => setHelpModalVisible(true)}
                  >
                    <QuestionCircleOutlined /> {getTranslation('查看帮助', 'View Help')}
                  </Button>
                </Space>
              </div>
            )}
          </div>
        </div>
        
        {/* 期刊等级查询结果 */}
        {renderJournalRanks()}
      </Card>
    );
  };

  // 渲染搜索结果
  const renderResults = () => {
    if (results.length === 0) {
      return (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={getTranslation('暂无搜索结果', 'No search results')}
        />
      );
    }

    return (
      <div>
        {results.map((result, index) => {
          // 检查是否为系统提示消息（失败结果）
          if (result.authors && result.authors.some(author => author.includes('系统提示'))) {
            return renderFailureCard(result);
          }
          
          // 正常结果卡片
          return (
            <Card 
              key={`result-${index}`}
              style={{ marginBottom: 16 }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <Title level={5} style={{ color: token.colorText, marginTop: 0, marginBottom: 8 }}>
                    {result.title}
                  </Title>
                  
                  {/* 期刊等级标签 - 移到标题下面 */}
                  {renderJournalRankBadges(result)}
                  
                  <Paragraph style={{ marginTop: 12 }}>{result.abstract}</Paragraph>
                  
                  {/* 论文信息 */}
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    {result.authors && result.authors.length > 0 && (
                      <div>
                        <Text type="secondary"><UserOutlined /> 作者: </Text>
                        <Text>{Array.isArray(result.authors) ? result.authors.join(', ') : result.authors}</Text>
                      </div>
                    )}
                    
                    {result.journal && (
                      <div>
                        <Text type="secondary"><BookOutlined /> 期刊: </Text>
                        <Text strong style={{ color: token.colorPrimary }}>{result.journal}</Text>
                      </div>
                    )}
                    
                    {result.year && (
                      <div>
                        <Text type="secondary"><CalendarOutlined /> 年份: </Text>
                        <Text>{result.year}</Text>
                      </div>
                    )}
                    
                    {result.doi && (
                      <div>
                        <Text type="secondary"><LinkOutlined /> DOI: </Text>
                        <Text 
                          copyable={{
                            text: result.doi,
                            onCopy: () => messageApi.success(getTranslation('DOI已复制', 'DOI copied'))
                          }}
                        >
                          {result.doi}
                        </Text>
                      </div>
                    )}
                  </Space>
                  
                  {/* 操作按钮 */}
                  <div style={{ marginTop: 16 }}>
                    <Space>
                      {result.doi && (
                        <>
                          <Button 
                            type="primary" 
                            icon={<GlobalOutlined />} 
                            onClick={() => handleOpenScihub(result.doi)}
                          >
                            {getTranslation('直接访问', 'Direct Access')}
                          </Button>
                          {renderScihubDropdown(result.doi)}
                          <Button 
                            icon={<CopyOutlined />}
                            onClick={() => handleCopyDoi(result.doi)}
                          >
                            {getTranslation('复制DOI', 'Copy DOI')}
                          </Button>
                        </>
                      )}
                      <Button 
                        icon={<FileTextOutlined />}
                        onClick={() => handleAddToLibrary(result)}
                      >
                        {getTranslation('添加到文献库', 'Add to Library')}
                      </Button>
                    </Space>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    );
  };

  return (
    <div>
      {contextHolder}
      
      {/* 搜索表单 */}
      <Card style={{ marginBottom: 16, borderRadius: token.borderRadiusLG }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={14} md={16} lg={18}>
              <Input.Search
                placeholder={getTranslation("输入论文标题、DOI或关键词...", "Enter paper title, DOI or keywords...")}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onSearch={() => handleSearch()}
                enterButton
                size="large"
                loading={loading}
                prefix={<SearchOutlined />}
                style={{ borderRadius: token.borderRadiusSM }}
              />
            </Col>
            <Col xs={24} sm={10} md={8} lg={6}>
              <Input 
                placeholder={getTranslation("作者（可选）", "Author (optional)")}
                value={authorText}
                onChange={(e) => setAuthorText(e.target.value)}
                prefix={<UserOutlined />}
                style={{ borderRadius: token.borderRadiusSM }}
                onPressEnter={() => handleSearch()}
              />
            </Col>
          </Row>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <Button 
                icon={<HistoryOutlined />} 
                onClick={() => setIsHistoryDrawerVisible(true)}
                type="text"
              >
                {getTranslation("历史记录", "History")}
              </Button>
              
              <Button 
                icon={<QuestionCircleOutlined />} 
                onClick={() => setHelpModalVisible(true)}
                type="text"
              >
                {getTranslation("帮助", "Help")}
              </Button>
            </Space>
            
            <Text type="secondary" style={{ fontSize: 12 }}>
              {isDOI(searchText) ? 
                getTranslation("已检测到DOI格式", "DOI format detected") : 
                getTranslation("未检测到DOI格式", "No DOI format detected")}
            </Text>
          </div>
        </Space>
      </Card>
      
      {/* 搜索结果 */}
      {renderResults()}

      {/* 搜索历史抽屉 */}
      <Drawer
        title={getTranslation('搜索历史', 'Search History')}
        placement="right"
        onClose={() => setIsHistoryDrawerVisible(false)}
        open={isHistoryDrawerVisible}
        width={350}
      >
        {searchHistory.length > 0 ? (
          <>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
                      <Button 
                type="primary" 
                danger 
                size="small" 
                icon={<DeleteOutlined />} 
                onClick={clearSearchHistory}
              >
                {getTranslation('清空历史', 'Clear History')}
                      </Button>
            </div>
            
            {searchHistory.map((item, index) => (
              <Card 
                key={`drawer-history-${index}`}
                style={{ 
                  marginBottom: 16,
                  cursor: 'pointer',
                  borderColor: getThemedStyle(token.colorBorderSecondary, token.colorBorder)
                }}
                hoverable
                onClick={() => applyHistorySearch(item)}
              >
                <div>
                  <Text strong style={{ color: getThemedStyle(token.colorText, token.colorTextLightSolid) }}>{item.keyword}</Text>
                  {item.author && (
                    <Tag color="green" style={{ marginLeft: 8 }}>
                      {item.author}
                    </Tag>
                  )}
                  <div style={{ marginTop: 4, fontSize: 12, color: token.colorTextSecondary }}>
                    {formatTimestamp(item.timestamp)}
                  </div>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
                                  <Button 
                    type="text" 
                    danger 
                                    size="small" 
                    icon={<DeleteOutlined />} 
                                    onClick={(e) => {
                                      e.stopPropagation();
                      const newHistory = searchHistory.filter((_, i) => i !== index);
                      setSearchHistory(newHistory);
                      saveSearchHistory(newHistory);
                    }}
                  />
                  <Button 
                    type="primary" 
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      applyHistorySearch(item);
                    }}
                  >
                    {getTranslation('应用搜索', 'Apply Search')}
                  </Button>
                          </div>
              </Card>
            ))}
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: token.colorTextSecondary }}>
            {getTranslation('暂无搜索历史', 'No search history')}
      </div>
        )}
      </Drawer>

      {/* 添加到文献库的模态框 */}
      <Modal
        title={
          <div style={{ 
            borderBottom: `1px solid ${getThemedStyle(token.colorBorderSecondary, token.colorBorder)}`,
            paddingBottom: '12px'
          }}>
            <Text strong style={{ fontSize: 16 }}>
              <FileTextOutlined style={{ marginRight: 8 }} />
              {getTranslation('添加到文献库', 'Add to Library')}
            </Text>
        </div>
        }
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={600}
        styles={{
          body: {
            background: getThemedStyle(token.colorBgContainer, token.colorBgElevated),
            padding: '24px 24px 12px'
          },
          mask: {
            background: isDarkMode ? 'rgba(0, 0, 0, 0.6)' : 'rgba(0, 0, 0, 0.45)'
          },
          content: {
            boxShadow: token.boxShadowSecondary,
            borderRadius: token.borderRadiusLG
          }
        }}
      >
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          requiredMark="optional"
        >
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="title"
                label={getTranslation('标题', 'Title')}
                rules={[{ required: true }]}
              >
                <Input style={{ borderRadius: token.borderRadiusSM }} />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="authors"
                label={getTranslation('作者', 'Authors')}
                rules={[{ required: true }]}
              >
          <Input
                  style={{ borderRadius: token.borderRadiusSM }} 
                  prefix={<TeamOutlined style={{ color: token.colorTextSecondary }} />}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col lg={16} md={16} sm={24} xs={24}>
              <Form.Item
                name="journal"
                label={getTranslation('期刊', 'Journal')}
              >
                <Input 
                  style={{ borderRadius: token.borderRadiusSM }} 
                  prefix={<BookOutlined style={{ color: token.colorTextSecondary }} />}
                />
              </Form.Item>
            </Col>
            <Col lg={8} md={8} sm={24} xs={24}>
              <Form.Item
                name="year"
                label={getTranslation('年份', 'Year')}
                rules={[{ required: true }]}
              >
                <Input 
                  type="number" 
                  style={{ borderRadius: token.borderRadiusSM }} 
                  prefix={<CalendarOutlined style={{ color: token.colorTextSecondary }} />}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="doi"
                label="DOI"
              >
                <Input 
                  style={{ borderRadius: token.borderRadiusSM }} 
                  prefix={<LinkOutlined style={{ color: token.colorTextSecondary }} />}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="abstract"
                label={getTranslation('摘要', 'Abstract')}
              >
                <Input.TextArea 
                  rows={4} 
                  style={{ 
                    borderRadius: token.borderRadiusSM,
                    background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillTertiary)
                  }} 
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="project_id"
                label={getTranslation('关联项目', 'Link to Project')}
              >
                    <Select
                  placeholder={getTranslation('选择项目（可选）', 'Select a project (optional)')} 
                      allowClear
                  loading={projectsLoading}
                  style={{ borderRadius: token.borderRadiusSM }}
                  suffixIcon={<LinkOutlined style={{ color: token.colorPrimary }} />}
                    >
                      {projects.map(project => (
                    <Option key={project.id} value={project.id}>{project.name}</Option>
                      ))}
                    </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Divider style={{ margin: '16px 0' }} />
          
          <Row gutter={16}>
            <Col span={24} style={{ textAlign: 'right' }}>
                      <Button
                onClick={() => setIsModalVisible(false)} 
                style={{ 
                  marginRight: 8,
                  borderRadius: token.borderRadiusSM
                }}
              >
                {getTranslation('取消', 'Cancel')}
                      </Button>
                    <Button
                      type="primary"
                htmlType="submit"
                style={{ borderRadius: token.borderRadiusSM }}
                    >
                {getTranslation('保存', 'Save')}
                    </Button>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 搜索历史详情模态框 */}
      <Modal 
        title={getTranslation('搜索详情', 'Search Details')}
        open={isHistoryModalVisible}
        onCancel={() => setIsHistoryModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsHistoryModalVisible(false)}>
            {getTranslation('取消', 'Cancel')}
          </Button>,
                  <Button
            key="apply" 
            type="primary" 
            onClick={() => selectedHistory && applyHistorySearch(selectedHistory)}
                  >
            {getTranslation('应用此搜索', 'Apply This Search')}
                  </Button>
        ]}
        styles={{
          body: {
            background: getThemedStyle(token.colorBgContainer, token.colorBgElevated)
          },
          mask: {
            background: isDarkMode ? 'rgba(0, 0, 0, 0.6)' : 'rgba(0, 0, 0, 0.45)'
          },
          content: {
            boxShadow: token.boxShadowSecondary
          }
        }}
      >
        {selectedHistory && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>{getTranslation('搜索关键词', 'Search Keyword')}</Text>
              <div style={{ 
                padding: '8px 12px', 
                background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillSecondary),
                borderRadius: token.borderRadiusLG,
                marginTop: 8
              }}>
                {selectedHistory.keyword}
              </div>
            </div>

            {selectedHistory.author && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>{getTranslation('作者', 'Author')}</Text>
                <div style={{ 
                  padding: '8px 12px', 
                  background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillSecondary),
                  borderRadius: token.borderRadiusLG,
                  marginTop: 8
                }}>
                  {selectedHistory.author}
              </div>
              </div>
            )}

            <div style={{ marginBottom: 16 }}>
              <Text strong>{getTranslation('搜索时间', 'Search Time')}</Text>
              <div style={{ 
                padding: '8px 12px', 
                background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillSecondary),
                borderRadius: token.borderRadiusLG,
                marginTop: 8
              }}>
                {formatTimestamp(selectedHistory.timestamp)}
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{getTranslation('搜索类型', 'Search Type')}</Text>
              <div style={{ 
                padding: '8px 12px', 
                background: getThemedStyle(token.colorBgContainerDisabled, token.colorFillSecondary),
                borderRadius: token.borderRadiusLG,
                marginTop: 8
              }}>
                {isDOI(selectedHistory.keyword) 
                  ? getTranslation('DOI搜索 (SciHub)', 'DOI Search (SciHub)')
                  : selectedHistory.author 
                    ? getTranslation('标题和作者搜索 (SciHub)', 'Title and Author Search (SciHub)')
                    : getTranslation('标题搜索 (谷歌学术)', 'Title Search (Google Scholar)')}
              </div>
            </div>
        </div>
      )}
      </Modal>

      {/* 帮助模态框 */}
      <HelpInfoModal
        visible={helpModalVisible}
        onClose={() => setHelpModalVisible(false)}
      />
    </div>
  );
};

export default ScihubSearch; 