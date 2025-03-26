// 导出核心API实例和工具函数
import { api, errorMessageManager, ensureString } from './core';
import { paperApi } from './paperApi';
import { projectApi } from './projectApi';
import { noteApi } from './noteApi';
import { knowledgeGraphApi } from './knowledgeGraphApi';
import { authApi } from './authApi';
import { searchApi } from './searchApi';
import { userApi } from './userApi';
import { journalApi } from './journalApi';
import { recommendationApi } from './recommendationApi';
import { scihubApi } from './scihubApi';
import { publicationRankApi } from './publicationRankApi';

export { api, errorMessageManager, ensureString } from './core';

// 导出所有类型定义
export * from './types';

// 导出所有API模块
export { paperApi } from './paperApi';
export { projectApi } from './projectApi';
export { noteApi } from './noteApi';
export { knowledgeGraphApi } from './knowledgeGraphApi';
export { authApi } from './authApi';
export { searchApi } from './searchApi';
export { userApi } from './userApi';
export { journalApi } from './journalApi';
export { recommendationApi } from './recommendationApi';
export { scihubApi } from './scihubApi';
export { publicationRankApi } from './publicationRankApi';

// 为errorManager提供一个别名，与旧代码兼容
export const errorManager = errorMessageManager;

// 创建scholarApi对象
// 静态定义scholarApi以避免动态导入问题
export const scholarApi = {
  searchPaper: async (title: string, author?: string) => {
    console.warn('scholarApi已被弃用，请使用替代方案');
    return [];
  },
  parseSearchResults: (html: string, originalTitle: string, originalAuthor?: string) => {
    console.warn('scholarApi已被弃用，请使用替代方案');
    return [];
  },
  extractPaperInfo: (results: any) => {
    console.warn('scholarApi已被弃用，请使用替代方案');
    return null;
  },
  calculateSimilarity: (str1: string, str2: string) => {
    console.warn('scholarApi已被弃用，请使用替代方案');
    return 0;
  }
};

// 尝试加载完整版scholarApi（如果存在）
try {
  // 使用动态导入尝试导入完整API
  import('./scholarApi').then(module => {
    // 将加载的方法合并到已导出的对象中
    Object.assign(scholarApi, module.scholarApi);
  }).catch(() => {
    console.warn('完整版scholarApi模块导入失败，使用替代实现');
  });
} catch (e) {
  console.warn('scholarApi模块导入失败，使用替代实现', e);
}

// 导出一个合并后的API对象，用于保持与旧代码的兼容性
export default {
  ...paperApi,
  ...projectApi,
  ...noteApi,
  ...knowledgeGraphApi,
  ...authApi,
  ...searchApi,
  ...userApi,
  ...journalApi,
  ...recommendationApi,
  ...scihubApi,
  ...publicationRankApi,
  ...scholarApi,
  // 添加一些原始的axios方法，以确保完全兼容
  get: api.get,
  post: api.post,
  put: api.put,
  delete: api.delete,
  patch: api.patch,
  request: api.request,
  defaults: api.defaults
}; 