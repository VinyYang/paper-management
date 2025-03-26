import axios from 'axios';
import { API_URL } from '../config';

interface Paper {
  id: number;
  title: string;
  authors: string;
  year?: number;
  journal?: string;
  abstract?: string;
  doi?: string;
  keywords?: string[];
  created_at: string;
  updated_at: string;
}

interface PaperCreateParams {
  title: string;
  authors: string;
  year?: number;
  journal?: string;
  abstract?: string;
  doi?: string;
  keywords?: string[];
}

interface PaperUpdateParams {
  title?: string;
  authors?: string;
  year?: number;
  journal?: string;
  abstract?: string;
  doi?: string;
  keywords?: string[];
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 论文相关API
export const paperApi = {
  // 获取论文列表
  getPapers: async (): Promise<ApiResponse<Paper[]>> => {
    const response = await axios.get(`${API_URL}/papers`);
    return response.data;
  },

  // 获取单篇论文详情
  getPaper: async (id: number): Promise<ApiResponse<Paper>> => {
    const response = await axios.get(`${API_URL}/papers/${id}`);
    return response.data;
  },

  // 创建论文
  createPaper: async (params: PaperCreateParams): Promise<ApiResponse<Paper>> => {
    const response = await axios.post(`${API_URL}/papers`, params);
    return response.data;
  },

  // 更新论文
  updatePaper: async (id: number, params: PaperUpdateParams): Promise<ApiResponse<Paper>> => {
    const response = await axios.put(`${API_URL}/papers/${id}`, params);
    return response.data;
  },

  // 删除论文
  deletePaper: async (id: number): Promise<ApiResponse<null>> => {
    const response = await axios.delete(`${API_URL}/papers/${id}`);
    return response.data;
  },

  // 获取项目中的论文
  getProjectPapers: async (projectId: number): Promise<ApiResponse<Paper[]>> => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/papers`);
    return response.data;
  },

  // 将论文添加到项目
  addPaperToProject: async (projectId: number, paperId: number): Promise<ApiResponse<any>> => {
    const response = await axios.post(`${API_URL}/projects/${projectId}/papers/${paperId}`);
    return response.data;
  },

  // 从项目中移除论文
  removePaperFromProject: async (projectId: number, paperId: number): Promise<ApiResponse<any>> => {
    const response = await axios.delete(`${API_URL}/projects/${projectId}/papers/${paperId}`);
    return response.data;
  },
}; 