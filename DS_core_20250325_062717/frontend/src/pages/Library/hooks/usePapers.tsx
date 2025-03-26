import { useState, useEffect, useCallback } from 'react';
import { message } from 'antd';
import { paperApi } from '../../../api/paper';
import { useTranslation } from 'react-i18next';

// 导出Paper接口
export interface Paper {
  id: number;
  title: string;
  authors: string;
  journal?: string;
  year?: number;
  doi?: string;
  abstract?: string;
  keywords?: string;
  created_at: string;
  updated_at: string;
}

export default function usePapers(projectId: number | null = null) {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const { i18n } = useTranslation();
  
  const getTranslation = useCallback((zhText: string, enText: string) => {
    return i18n.language === 'zh' ? zhText : enText;
  }, [i18n.language]);

  // 获取文献列表
  const fetchPapers = useCallback(async () => {
    setLoading(true);
    try {
      let response;
      if (projectId) {
        response = await paperApi.getProjectPapers(projectId);
      } else {
        response = await paperApi.getPapers();
      }
      
      if (response.code === 200) {
        // 确保类型与Paper接口一致
        const parsedPapers = (response.data || []).map((paper: any) => ({
          ...paper,
          keywords: typeof paper.keywords === 'object' ? paper.keywords.join(', ') : paper.keywords
        }));
        setPapers(parsedPapers);
      } else {
        message.error(response.message || getTranslation('获取文献列表失败', 'Failed to get paper list'));
      }
    } catch (error) {
      console.error('获取文献列表出错:', error);
      message.error(getTranslation('获取文献列表出错', 'Error getting paper list'));
    } finally {
      setLoading(false);
    }
  }, [projectId, getTranslation]);

  // 添加文献
  const addPaper = useCallback(async (paperData: any) => {
    setLoading(true);
    try {
      let paperId: number | null = null;

      // 1. 先创建文献记录
      const response = await paperApi.createPaper(paperData);
      if (response.code !== 200) {
        message.error(response.message || getTranslation('创建文献失败', 'Failed to create paper'));
        setLoading(false);
        return null;
      }

      paperId = response.data.id;
      
      // 2. 如果有项目ID且创建成功，添加到项目
      if (projectId && paperId) {
        const addToProjectResponse = await paperApi.addPaperToProject(projectId, paperId);
        if (addToProjectResponse.code !== 200) {
          message.warning(getTranslation('文献已创建，但添加到项目失败', 'Paper created but failed to add to project'));
        }
      }

      message.success(getTranslation('文献创建成功', 'Paper created successfully'));

      // 刷新文献列表
      await fetchPapers();
      return paperId;
    } catch (error) {
      console.error('添加文献出错:', error);
      message.error(getTranslation('添加文献出错', 'Error adding paper'));
      return null;
    } finally {
      setLoading(false);
    }
  }, [projectId, fetchPapers, getTranslation]);

  // 更新文献
  const updatePaper = useCallback(async (paperId: number, paperData: any) => {
    setLoading(true);
    try {
      const response = await paperApi.updatePaper(paperId, paperData);
      
      if (response.code === 200) {
        message.success(getTranslation('更新文献成功', 'Paper updated successfully'));
        await fetchPapers();
        return true;
      } else {
        message.error(response.message || getTranslation('更新文献失败', 'Failed to update paper'));
        return false;
      }
    } catch (error) {
      console.error('更新文献出错:', error);
      message.error(getTranslation('更新文献出错', 'Error updating paper'));
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchPapers, getTranslation]);

  // 删除文献
  const deletePaper = useCallback(async (paperId: number) => {
    setLoading(true);
    try {
      const response = await paperApi.deletePaper(paperId);
      
      if (response.code === 200) {
        message.success(getTranslation('删除文献成功', 'Paper deleted successfully'));
        await fetchPapers();
        return true;
      } else {
        message.error(response.message || getTranslation('删除文献失败', 'Failed to delete paper'));
        return false;
      }
    } catch (error) {
      console.error('删除文献出错:', error);
      message.error(getTranslation('删除文献出错', 'Error deleting paper'));
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchPapers, getTranslation]);

  // 从项目中移除文献
  const removePaperFromProject = useCallback(async (paperId: number) => {
    if (!projectId) return false;
    
    setLoading(true);
    try {
      const response = await paperApi.removePaperFromProject(projectId, paperId);
      
      if (response.code === 200) {
        message.success(getTranslation('从项目中移除文献成功', 'Paper removed from project successfully'));
        await fetchPapers();
        return true;
      } else {
        message.error(response.message || getTranslation('从项目中移除文献失败', 'Failed to remove paper from project'));
        return false;
      }
    } catch (error) {
      console.error('从项目中移除文献出错:', error);
      message.error(getTranslation('从项目中移除文献出错', 'Error removing paper from project'));
      return false;
    } finally {
      setLoading(false);
    }
  }, [projectId, fetchPapers, getTranslation]);

  useEffect(() => {
    fetchPapers();
  }, [fetchPapers]);

  return {
    papers,
    loading,
    fetchPapers,
    addPaper,
    updatePaper,
    deletePaper,
    removePaperFromProject,
    getTranslation
  };
} 