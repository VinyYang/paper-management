// 此文件保留用于向后兼容性，但所有内容都重定向到新的模块化API
// 要直接使用新API，请导入：import { paperApi, projectApi, ... } from './api/';

import defaultApi, { 
  api as axiosInstance, 
  errorMessageManager,
  errorManager,
  paperApi,
  projectApi,
  noteApi,
  knowledgeGraphApi,
  authApi,
  searchApi,
  userApi,
  journalApi,
  recommendationApi,
  scihubApi,
  publicationRankApi
} from './api/';

// 对外导出错误消息管理器
export { errorMessageManager, errorManager };

// 重新导出所有模块化API
export {
  paperApi,
  projectApi,
  noteApi,
  knowledgeGraphApi,
  authApi,
  searchApi,
  userApi,
  journalApi,
  recommendationApi,
  scihubApi,
  publicationRankApi
};

// 导出向后兼容的axios实例
export const api = axiosInstance;

// 导出向后兼容的默认API对象
export default defaultApi; 