import { api } from './core';
import { Feedback } from './types';

// 推荐相关API
export const recommendationApi = {
  getRecommendations: (limit: number = 10) => {
    return api.get(`/api/recommendations?limit=${limit}`);
  },
  
  refreshRecommendations: () => {
    return api.post('/api/recommendations/refresh');
  },
  
  forceRefreshRecommendations: () => {
    return api.post('/api/recommendations/force-refresh');
  },
  
  getRandomRecommendations: (category?: string, limit: number = 10) => {
    let url = `/api/recommendations/random/?limit=${limit}`;
    if (category && category !== '全部') {
      url += `&category=${encodeURIComponent(category)}`;
    }
    // 将随机推荐的结果包装成与getRecommendations一致的格式
    return api.get(url).then(response => {
      // 检查响应数据的格式
      if (Array.isArray(response.data)) {
        // 如果响应是数组，将其包装成期望的格式
        return {
          ...response,
          data: {
            recommendations: response.data
          }
        };
      } else if (response.data && Array.isArray(response.data.recommendations)) {
        // 如果响应已经是期望的格式，直接返回
        return response;
      } else {
        // 如果都不是，返回空数组
        console.error('随机推荐API返回的数据格式不正确:', response.data);
        return {
          ...response,
          data: {
            recommendations: []
          }
        };
      }
    }).catch(error => {
      console.error('获取随机推荐失败:', error);
      // 返回一个包含空推荐数组的响应对象
      return {
        data: {
          recommendations: []
        }
      };
    });
  },
  
  getUserStats: () => 
    api.get('/api/recommendations/stats'),
  getUserInterests: () => 
    api.get('/api/recommendations/interests'),
  markAsRead: (paperId: number) => 
    api.post(`/api/recommendations/${paperId}/read`),
  submitFeedback: (data: Feedback) => 
    api.post('/api/recommendations/feedback', data),
  forceRefreshRandomRecommendations: (category?: string, limit: number = 10) => {
    let url = `/api/recommendations/random/force-refresh?limit=${limit}`;
    if (category && category !== '全部') {
      url += `&category=${encodeURIComponent(category)}`;
    }
    return api.post(url);
  },
}; 