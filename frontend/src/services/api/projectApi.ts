import { api } from './core';
import { Project, ProjectCreateParams } from './types';

// 项目相关API
export const projectApi = {
  getProjects: async () => {
    const response = await api.get('/api/projects/');
    return response.data;
  },

  getProject: async (id: number) => {
    const response = await api.get(`/api/projects/${id}`);
    return response.data;
  },

  createProject: async (data: ProjectCreateParams) => {
    const response = await api.post('/api/projects/', data);
    return response.data;
  },

  updateProject: async (id: number, data: Project) => {
    const response = await api.put(`/api/projects/${id}`, data);
    return response.data;
  },

  deleteProject: async (id: number) => {
    await api.delete(`/api/projects/${id}`);
  },

  getProjectPapers: async (id: number) => {
    const response = await api.get(`/api/projects/${id}/papers`);
    return response.data;
  },

  addPaper: async (projectId: number, paperId: number) => {
    try {
      console.log(`添加论文[${paperId}]到项目[${projectId}]`);
      
      // 确保参数有效
      if (!projectId || !paperId) {
        throw new Error("项目ID或论文ID无效");
      }
      
      // 尝试使用POST请求
      const response = await api.post(`/api/projects/${projectId}/papers/${paperId}`);
      console.log('API响应:', response);
      
      // 添加成功后，获取项目详情确认关联关系已建立
      try {
        const projectDetails = await api.get(`/api/projects/${projectId}`);
        console.log(`项目[${projectId}]详情:`, projectDetails.data);
      } catch (e) {
        console.warn(`获取项目[${projectId}]详情失败:`, e);
      }
      
      return response.data;
    } catch (error) {
      console.error(`将论文 ${paperId} 添加到项目 ${projectId} 失败:`, error);
      throw error;
    }
  },

  removePaper: async (projectId: number, paperId: number) => {
    await api.delete(`/api/projects/${projectId}/papers/${paperId}`);
  }
}; 