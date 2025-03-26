import { api } from './core';
import { Paper, PaperData, ApiResponse } from './types';

// 论文相关API
export const paperApi = {
  getPapers: (params = {}) => api.get('/api/papers/', { params }).then(response => {
    // 处理API返回的数据，确保保留所有字段
    if (response.data && response.data.papers) {
      response.data.papers = response.data.papers.map((paper: Paper) => ({
        ...paper
      }));
    } else if (Array.isArray(response.data)) {
      response.data = response.data.map((paper: Paper) => ({
        ...paper
      }));
    }
    console.log('获取论文数据:', response.data); // 添加日志
    return response;
  }),
  
  createPaper: (paper: PaperData, pdfFile?: FormData) => {
    if (pdfFile) {
      // 添加论文元数据
      const formData = new FormData();
      formData.append('paper_data', JSON.stringify(paper));
      // 获取文件对象
      const fileFromFormData = pdfFile.get('file');
      if (fileFromFormData) {
        formData.append('pdf_file', fileFromFormData);
      }
      return api.post('/api/papers/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } else {
      console.log('创建论文，数据:', paper); // 添加日志
      return api.post('/api/papers/', paper);
    }
  },
  
  getPaper: (id: number) => api.get(`/api/papers/${id}`).then(response => {
    // 处理API返回的数据，确保设置has_pdf属性
    if (response.data) {
      response.data = {
        ...response.data,
        has_pdf: !!response.data.local_pdf_path
      };
    }
    return response;
  }),
  
  updatePaper: (id: number, paper: PaperData) => api.put(`/api/papers/${id}`, paper),
  
  deletePaper: (id: number) => api.delete(`/api/papers/${id}`),
  
  searchPapers: (query: string) => api.get(`/api/papers/search?q=${query}`),
  
  searchByDoi: (doi: string) => api.get(`/api/papers/doi/${doi}`),
  
  uploadPdf: (paperId: number, formData: FormData) => api.post(`/api/papers/${paperId}/upload-pdf`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then(response => {
    // 确保返回的数据包含必要的PDF信息
    if (response.data && response.data.local_pdf_path) {
      response.data.has_pdf = true;
    }
    return response;
  }),
  
  downloadPdf: (paperId: number, options: { download?: boolean } = {}) => api.get(`/api/papers/${paperId}/pdf`, {
    ...options,
    responseType: 'blob'
  }).then(response => {
    // 如果设置了download选项，则触发下载
    if (options.download) {
      // 创建临时URL
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // 设置文件名
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'paper.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // 清理
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
    return response;
  }),
  
  // 添加PDF获取方法，用于在线查看而非下载
  getPdf: (paperId: number, options = {}) => 
    api.get(`/api/papers/${paperId}/pdf`, {
      ...options,
      responseType: 'blob'
    }),
  
  // 添加删除PDF的方法
  deletePdf: (paperId: number) => api.delete(`/api/papers/${paperId}/pdf`),
  
  getStorageInfo: () => api.get('/api/storage-info'),
  
  getPaperNotes: (paperId: number) => 
    api.get(`/api/papers/${paperId}/notes`),
  
  // 处理项目相关的论文
  getProjectPapers: async (projectId: number): Promise<ApiResponse<Paper[]>> => {
    try {
      const response = await api.get(`/api/projects/${projectId}/papers`);
      return response.data;
    } catch (error) {
      console.error(`获取项目 ${projectId} 的文献列表失败:`, error);
      throw error;
    }
  },
  
  // 将论文添加到项目
  addPaperToProject: async (projectId: number, paperId: number): Promise<ApiResponse<null>> => {
    try {
      const response = await api.post(`/api/projects/${projectId}/papers`, { paper_id: paperId });
      return response.data;
    } catch (error) {
      console.error(`将文献 ${paperId} 添加到项目 ${projectId} 失败:`, error);
      throw error;
    }
  },
  
  // 从项目中移除论文
  removePaperFromProject: async (projectId: number, paperId: number): Promise<ApiResponse<null>> => {
    try {
      const response = await api.delete(`/api/projects/${projectId}/papers/${paperId}`);
      return response.data;
    } catch (error) {
      console.error(`从项目 ${projectId} 移除文献 ${paperId} 失败:`, error);
      throw error;
    }
  }
}; 