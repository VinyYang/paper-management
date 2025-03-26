import { api, ensureString } from './core';
import { SearchResult } from './types';

// 谷歌学术相关API
export const scholarApi = {
  // 国内可用的谷歌学术镜像站点
  scholarMirrors: [
    'https://xueshu.lanfanshu.cn',
    'https://ac.scmor.com',
    'https://scholar.hedasudi.com',
    'https://gg.xueshu5.com'
  ],
  
  // 获取随机镜像站点
  getRandomMirror: (): string => {
    const mirrors = scholarApi.scholarMirrors;
    const randomIndex = Math.floor(Math.random() * mirrors.length);
    return mirrors[randomIndex];
  },
  
  // 计算两个字符串的相似度（使用Levenshtein距离的归一化版本）
  calculateSimilarity: (str1: string, str2: string): number => {
    if (!str1 || !str2) return 0;
    
    const a = str1.toLowerCase();
    const b = str2.toLowerCase();
    
    // 使用编辑距离算法
    const matrix = [];
    
    // 初始化
    for (let i = 0; i <= a.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= b.length; j++) {
      matrix[0][j] = j;
    }
    
    // 填充矩阵
    for (let i = 1; i <= a.length; i++) {
      for (let j = 1; j <= b.length; j++) {
        if (a.charAt(i - 1) === b.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1, // 替换
            matrix[i][j - 1] + 1,     // 插入
            matrix[i - 1][j] + 1      // 删除
          );
        }
      }
    }
    
    // 计算相似度（1 - 归一化编辑距离）
    const maxLen = Math.max(a.length, b.length);
    const similarity = 1 - matrix[a.length][b.length] / maxLen;
    
    return similarity;
  },

  // 在谷歌学术上搜索论文
  searchPaper: async (title: string, author?: string): Promise<SearchResult[]> => {
    try {
      // 构建搜索查询
      let query = `allintitle:${title}`;
      if (author) {
        query += ` author:${author}`;
      }
      
      // 使用后端API进行搜索，后端将使用配置的镜像站点
      const response = await api.get('/api/search/scholar', {
        params: { q: query },
        timeout: 30000 // 30秒超时
      });
      
      // 处理返回数据
      if (response.data && response.data.results) {
        // 新版API直接返回结构化数据
        console.log('Search results:', response.data.results);
        return response.data.results;
      } else if (response.data && typeof response.data === 'string') {
        // 旧版API返回HTML，需要解析
        return scholarApi.parseSearchResults(response.data, title);
      } else {
        console.log('未知格式的搜索结果:', response.data);
        return [];
      }
    } catch (error) {
      console.error('Scholar search error:', error);
      return [];
    }
  },
  
  // 解析HTML响应
  parseSearchResults: (html: string, originalTitle: string): SearchResult[] => {
    // 创建一个临时的DOM元素来解析HTML
    const doc = document.implementation.createHTMLDocument('temp');
    doc.documentElement.innerHTML = html;
    
    const results: SearchResult[] = [];
    
    // 尝试不同的选择器（因为谷歌学术的HTML结构可能发生变化）
    const selectors = [
      '.gs_ri', // 标准结果项
      '.gs_r.gs_or.gs_scl', // 备用选择器1
      '.gs_or.gs_scl' // 备用选择器2
    ];
    
    let items: NodeListOf<Element> | null = null;
    
    // 尝试不同的选择器，直到找到结果
    for (const selector of selectors) {
      items = doc.querySelectorAll(selector);
      if (items && items.length > 0) {
        console.log(`找到选择器 ${selector} 的结果：${items.length}项`);
        break;
      }
    }
    
    if (!items || items.length === 0) {
      console.warn('无法在HTML中找到论文结果');
      return [];
    }
    
    // 处理每个找到的结果
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
      const paperInfo = scholarApi.extractPaperInfo(item, originalTitle);
      if (paperInfo) {
        results.push(paperInfo);
      }
    }
    
    // 不再按相似度排序，直接返回结果
    return results;
  },
  
  // 从搜索结果中提取论文信息
  extractPaperInfo: (item: Element, originalTitle: string): SearchResult | null => {
    try {
      // 尝试获取标题元素
      const titleEl = item.querySelector('.gs_rt a, .gs_rti a') || 
                     item.querySelector('[data-lid]') ||
                     item.querySelector('h3 a');
      
      if (!titleEl) {
        return null;
      }
      
      const title = ensureString(titleEl.textContent).trim();
      const link = ensureString(titleEl.getAttribute('href'));
      
      // 尝试获取摘要
      const abstractEl = item.querySelector('.gs_rs') || 
                        item.querySelector('.gs_fl') || 
                        item.querySelector('.gs_snippet');
      const abstract = abstractEl ? ensureString(abstractEl.textContent).trim() : '';
      
      // 尝试获取作者、期刊、年份信息
      const infoEl = item.querySelector('.gs_a') || 
                    item.querySelector('.gs_fl');
      const info = infoEl ? ensureString(infoEl.textContent).trim() : '';
      
      // 尝试解析DOI
      let doi = '';
      
      // 方法1：从文本中查找DOI
      const doiMatch = abstract.match(/10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i) || 
                      info.match(/10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i);
      
      if (doiMatch) {
        doi = doiMatch[0];
      }
      
      // 方法2：查找外部链接中的DOI
      if (!doi) {
        const links = item.querySelectorAll('a');
        for (let i = 0; i < links.length; i++) {
          const href = links[i].getAttribute('href') || '';
          const doiLinkMatch = href.match(/10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i);
          if (doiLinkMatch) {
            doi = doiLinkMatch[0];
            break;
          }
        }
      }
      
      // 计算标题相似度
      const similarity = scholarApi.calculateSimilarity(title, originalTitle);
      
      return {
        id: Math.random(), // 生成一个随机ID
        title,
        authors: [], // 从info解析作者，但这里简化处理
        year: 0, // 这里应该从info中解析，但简化处理
        journal: info,
        abstract,
        doi,
        url: link,
        source: 'scholar'
      };
    } catch (error) {
      console.error('提取论文信息时出错:', error);
      return null;
    }
  }
}; 