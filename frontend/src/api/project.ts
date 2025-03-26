import { api } from './api';

export interface Project {
  id: number;
  name: string;
  description?: string;
  is_public?: boolean;
  created_at?: string;
  updated_at?: string;
  user_id?: number;
}

export interface ProjectCreateParams {
  name: string;
  description?: string;
  is_public?: boolean;
}

export interface ProjectUpdateParams {
  name?: string;
  description?: string;
  is_public?: boolean;
}

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export const projectApi = {
  // 获取项目列表
  getProjects: async (): Promise<ApiResponse<Project[]>> => {
    try {
      const response = await api.get('/api/projects');
      return response.data;
    } catch (error) {
      console.error('获取项目列表失败:', error);
      throw error;
    }
  },

  // 获取单个项目详情
  getProject: async (id: number): Promise<ApiResponse<Project>> => {
    try {
      const response = await api.get(`/api/projects/${id}`);
      return response.data;
    } catch (error) {
      console.error(`获取项目 ${id} 详情失败:`, error);
      throw error;
    }
  },

  // 创建新项目
  createProject: async (params: ProjectCreateParams): Promise<ApiResponse<Project>> => {
    try {
      const response = await api.post('/api/projects', params);
      return response.data;
    } catch (error) {
      console.error('创建项目失败:', error);
      throw error;
    }
  },

  // 更新项目
  updateProject: async (id: number, params: ProjectUpdateParams): Promise<ApiResponse<Project>> => {
    try {
      const response = await api.put(`/api/projects/${id}`, params);
      return response.data;
    } catch (error) {
      console.error(`更新项目 ${id} 失败:`, error);
      throw error;
    }
  },

  // 删除项目
  deleteProject: async (id: number): Promise<ApiResponse<null>> => {
    try {
      const response = await api.delete(`/api/projects/${id}`);
      return response.data;
    } catch (error) {
      console.error(`删除项目 ${id} 失败:`, error);
      throw error;
    }
  },
  
  // 获取项目中的论文列表
  getProjectPapers: async (projectId: number): Promise<ApiResponse<any[]>> => {
    try {
      const response = await api.get(`/api/projects/${projectId}/papers`);
      return response.data;
    } catch (error) {
      console.error(`获取项目 ${projectId} 的论文列表失败:`, error);
      throw error;
    }
  },
  
  // 将论文添加到项目中
  addPaperToProject: async (projectId: number, paperId: number): Promise<ApiResponse<null>> => {
    try {
      const response = await api.post(`/api/projects/${projectId}/papers/${paperId}`);
      return response.data;
    } catch (error) {
      console.error(`添加论文到项目 ${projectId} 失败:`, error);
      throw error;
    }
  },
  
  // 从项目中移除论文
  removePaperFromProject: async (projectId: number, paperId: number): Promise<ApiResponse<null>> => {
    try {
      const response = await api.delete(`/api/projects/${projectId}/papers/${paperId}`);
      return response.data;
    } catch (error) {
      console.error(`从项目 ${projectId} 移除论文失败:`, error);
      throw error;
    }
  }
}; 