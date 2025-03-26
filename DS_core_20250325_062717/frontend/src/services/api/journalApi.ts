import { api } from './core';

// 期刊相关API
export const journalApi = {
  getJournals: () => {
    return api.get('/api/journals');
  },
   
  initializeJournals: () => {
    return api.get('/api/journals/initialize');
  },
   
  getLatestPapers: (category?: string, limit: number = 10) => {
    let url = `/api/latest-papers?limit=${limit}`;
    if (category) {
      url += `&category=${encodeURIComponent(category)}`;
    }
    return api.get(url);
  },
   
  refreshLatestPapers: (limit: number = 3) => {
    return api.post(`/api/latest-papers/refresh?limit=${limit}`);
  },
   
  forceRefreshLatestPapers: (limit: number = 3) => {
    return api.post(`/api/latest-papers/force-refresh?limit=${limit}`);
  }
}; 