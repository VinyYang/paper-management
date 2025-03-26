import { api } from './core';
import { scihubApi } from './scihubApi';
import axios from 'axios';

// 定义搜索结果类型
export interface SearchResult {
  id?: number;
  title: string;
  authors: string[];
  year: number;
  journal?: string;
  abstract?: string;
  doi?: string;
  url?: string;
  source: string;
  has_pdf: boolean;
}

// 搜索相关API
export const searchApi = {
  // 可用的谷歌学术镜像站
  scholarMirrors: [
    "https://xueshu.lanfanshu.cn",  // 多平台推荐，稳定快速
    "https://ac.scmor.com",         // 集成Sci-Hub链接
    "https://scholar.hedasudi.com",  // 直接访问，界面简洁
    "https://gg.xueshu5.com"        // 简洁界面，加载快速
  ],

  // 搜索历史
  getSearchHistory: (limit: number = 10) => 
    api.get(`/api/search-history?limit=${limit}`),
  
  addSearchHistory: (query: string, type: string = 'doi') => 
    api.post('/api/search-history', { query, type }),
  
  deleteSearchHistory: (id: number) => 
    api.delete(`/api/search-history/${id}`),
  
  clearSearchHistory: () => 
    api.delete('/api/search-history'),
  
  // 期刊等级查询
  getPublicationRank: (publicationName: string) => 
    api.get(`/api/publication-rank/${encodeURIComponent(publicationName)}`),
  
  // 推荐系统
  getRecommendations: () => 
    api.get('/api/recommendations'),
  
  getRecommendationsByPaper: (paperId: number) => 
    api.get(`/api/recommendations/paper/${paperId}`),
  
  getSimilarPapers: (paperId: number) => 
    api.get(`/api/papers/${paperId}/similar`),
  
  // 文献搜索
  searchScholar: async (query: string): Promise<{data: SearchResult[]}> => {
    console.log('直接从谷歌学术镜像站搜索:', query);
    
    // 存储错误信息，如果所有镜像都失败，将返回这些错误
    const errors: Array<{mirror: string, error: string}> = [];
    
    // 尝试使用多种代理服务
    const corsProxies = [
      'https://corsproxy.io/?',
      'https://cors-anywhere.herokuapp.com/',
      'https://api.allorigins.win/raw?url=',
      'https://thingproxy.freeboard.io/fetch/',
      'https://api.codetabs.com/v1/proxy?quest=',
      'https://cors-proxy.htmldriven.com/?url=',
      'https://crossorigin.me/',
      ''  // 无代理直接请求（可能会因CORS限制失败）
    ];
    
    // 依次尝试每个镜像站
    for (const mirror of searchApi.scholarMirrors) {
      // 对每个镜像站，依次尝试不同的代理
      for (const corsProxy of corsProxies) {
        try {
          const baseUrl = `${mirror}/scholar?q=${encodeURIComponent(query)}`;
          const url = corsProxy + baseUrl;
          console.log(`尝试使用代理 ${corsProxy || '无代理'} 访问: ${baseUrl}`);
          
          // 创建一个带超时的请求
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
          
          let response;
          let html = '';
          
          try {
            // 尝试通过fetch API请求
            response = await fetch(url, {
              method: 'GET',
              headers: {
                'Origin': window.location.origin,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
              },
              signal: controller.signal,
              mode: corsProxy ? 'cors' : 'no-cors' // 无代理时尝试no-cors模式
            });
            
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            html = await response.text();
          } catch (fetchError) {
            console.log('Fetch失败，尝试使用axios:', fetchError);
            
            try {
              // 如果fetch失败，尝试使用axios
              const axiosResponse = await axios.get(url, {
                timeout: 10000,
                headers: {
                  'Origin': window.location.origin,
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
                }
              });
              
              if (axiosResponse.status !== 200) {
                throw new Error(`HTTP error! status: ${axiosResponse.status}`);
              }
              
              html = axiosResponse.data;
            } catch (axiosError) {
              throw axiosError;
            }
          } finally {
            clearTimeout(timeoutId);
          }
          
          if (!html) {
            throw new Error('未获取到任何内容');
          }
          
          // 解析HTML获取文章信息
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          
          // 查找所有文章条目 - 增加更多选择器以适应不同镜像站格式
          const articles = doc.querySelectorAll('.gs_r.gs_or.gs_scl') || 
                          doc.querySelectorAll('.result-container') ||
                          doc.querySelectorAll('div[data-aid]') || 
                          doc.querySelectorAll('.paper-container') ||
                          doc.querySelectorAll('.search-result') ||
                          doc.querySelectorAll('article') ||
                          doc.querySelectorAll('.gs_ri');
          
          if (!articles || articles.length === 0) {
            throw new Error('未找到任何文章');
          }
          
          const results: SearchResult[] = [];
          
          for (let i = 0; i < Math.min(10, articles.length); i++) {
            const article = articles[i];
            
            // 增加更多选择器来提高标题元素查找的成功率
            const titleElem = article.querySelector('.gs_rt') || 
                             article.querySelector('.title') ||
                             article.querySelector('h3') ||
                             article.querySelector('h4') ||
                             article.querySelector('a[data-clk="hl"]');
                             
            if (!titleElem) continue;
            
            let title = titleElem.textContent?.trim() || '';
            if (title.startsWith('[PDF]') || title.startsWith('[HTML]')) {
              title = title.substring(6).trim();
            }
            
            // 增加更多选择器来提高作者元素查找的成功率
            const metaElem = article.querySelector('.gs_a') || 
                            article.querySelector('.author') ||
                            article.querySelector('.gs_gray') ||
                            article.querySelector('.meta');
                            
            let authorList: string[] = [];
            let journal = '';
            let year = 0;
            
            if (metaElem) {
              const metaText = metaElem.textContent?.trim() || '';
              const authorMatch = metaText.match(/^(.*?)\s*-\s*/);
              if (authorMatch) {
                authorList = authorMatch[1].split(',').map(a => a.trim());
              }
              
              const yearMatch = metaText.match(/\b(19|20)\d{2}\b/);
              if (yearMatch) {
                year = parseInt(yearMatch[0]);
              }
              
              const journalMatch = metaText.match(/-\s*(.*?)\s*,/);
              if (journalMatch) {
                journal = journalMatch[1].trim();
              }
            }
            
            // 增加更多选择器来提高摘要元素查找的成功率
            const abstractElem = article.querySelector('.gs_rs') || 
                                article.querySelector('.abstract') ||
                                article.querySelector('.snippet') ||
                                article.querySelector('.gs_fl');
                                
            const abstract = abstractElem ? abstractElem.textContent?.trim() || '' : '';
            
            // 提取DOI (如果有)
            let doi = '';
            const links = article.querySelectorAll('a');
            
            // 使用数组方法迭代NodeList，避免for...of循环的兼容性问题
            Array.from(links).forEach(link => {
              const href = link.getAttribute('href') || '';
              // 增强DOI匹配模式
              const doiMatch = href.match(/10\.\d{4,}[\d\.]+\/[^&\s#]+/);
              if (doiMatch && !doi) { // 只获取第一个匹配的DOI
                doi = doiMatch[0];
              }
            });
            
            // 如果未从链接中找到DOI，尝试从文本中查找
            if (!doi) {
              const fullText = article.textContent || '';
              const doiMatches = fullText.match(/10\.\d{4,}[\d\.]+\/[^&\s#]+/g);
              if (doiMatches && doiMatches.length > 0) {
                doi = doiMatches[0];
              }
            }
            
            // 获取链接URL
            let url = '';
            const titleLink = titleElem.querySelector('a') || titleElem.tagName === 'A' ? titleElem : null;
            if (titleLink) {
              url = titleLink.getAttribute('href') || '';
              if (url && !url.startsWith('http')) {
                url = mirror + url;
              }
            }
            
            results.push({
              id: Math.floor(Math.random() * 1000000),
              title,
              authors: authorList,
              year,
              journal,
              abstract,
              doi,
              url,
              source: 'scholar',
              has_pdf: doi ? true : false // 如果有DOI，假设可能有PDF
            });
          }
          
          console.log('从谷歌学术成功获取搜索结果:', results);
          return { data: results };
          
        } catch (error) {
          console.error(`从 ${mirror} 使用代理 ${corsProxy || '无代理'} 获取失败:`, error);
          errors.push({ 
            mirror, 
            error: error instanceof Error ? error.message : String(error) 
          });
          // 继续尝试下一个代理
          continue;
        }
      }
      // 如果所有代理都失败，继续尝试下一个镜像站
    }
    
    // 如果所有镜像和代理都失败了
    console.error('所有谷歌学术镜像站均无法访问:', errors);
    return {
      data: [{
        id: Math.floor(Math.random() * 1000000),
        title: `搜索结果: ${query}`,
        authors: ['系统提示'],
        year: new Date().getFullYear(),
        journal: '提示信息',
        abstract: `无法从谷歌学术获取搜索结果。您可以尝试手动访问以下谷歌学术镜像站点: ${searchApi.scholarMirrors.join(', ')}`,
        doi: '',
        url: '',
        source: 'scholar',
        has_pdf: false
      }]
    };
  },
  
  searchByDoi: (doi: string) => 
    api.get(`/api/search/doi/${encodeURIComponent(doi)}`),
  
  // 专门用于DOI搜索
  searchDOI: async (doi: string): Promise<{data: SearchResult[]}> => {
    console.log('使用searchDOI函数搜索DOI:', doi);
    return await scihubApi.searchDOI(doi);
  },
  
  // Sci-Hub搜索
  searchScihub: async (query: string, author: string = ''): Promise<{data: SearchResult[]}> => {
    console.log('使用searchScihub函数搜索标题和作者:', query, author);
    return await scihubApi.searchScihub(query, author);
  },
  
  // EasyScholar搜索
  searchEasyScholar: (query: string) =>
    api.get(`/api/search/easyscholar?q=${encodeURIComponent(query)}`)
}; 