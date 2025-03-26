import { useState, useEffect, useCallback } from 'react';
import { message } from 'antd';
import { projectApi } from '../../../api/project';
import { useTranslation } from 'react-i18next';

interface Project {
  id: number;
  name: string;
}

export default function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const { i18n } = useTranslation();

  const getTranslation = useCallback((zhText: string, enText: string) => {
    return i18n.language === 'zh' ? zhText : enText;
  }, [i18n.language]);

  // 获取项目列表
  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const response = await projectApi.getProjects();
      if (response.code === 200) {
        setProjects(response.data || []);
      } else {
        message.error(getTranslation('获取项目列表失败', 'Failed to get project list'));
      }
    } catch (error) {
      console.error('获取项目列表出错:', error);
      message.error(getTranslation('获取项目列表出错', 'Error getting project list'));
    } finally {
      setLoading(false);
    }
  }, [getTranslation]);

  // 创建新项目
  const createProject = useCallback(async (name: string, description?: string) => {
    setLoading(true);
    try {
      const response = await projectApi.createProject({ name, description });
      if (response.code === 200 || response.code === 201) {
        message.success(getTranslation('项目创建成功', 'Project created successfully'));
        await fetchProjects();
        return true;
      } else {
        message.error(response.message || getTranslation('创建项目失败', 'Failed to create project'));
        return false;
      }
    } catch (error: any) {
      console.error('创建项目出错:', error);
      message.error(error.response?.data?.detail || getTranslation('创建项目出错', 'Error creating project'));
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchProjects, getTranslation]);

  // 更新项目
  const updateProject = useCallback(async (id: number, name: string) => {
    setLoading(true);
    try {
      const response = await projectApi.updateProject(id, { name });
      if (response.code === 200) {
        message.success(getTranslation('项目更新成功', 'Project updated successfully'));
        await fetchProjects();
      } else {
        message.error(response.message || getTranslation('更新项目失败', 'Failed to update project'));
      }
    } catch (error) {
      console.error('更新项目出错:', error);
      message.error(getTranslation('更新项目出错', 'Error updating project'));
    } finally {
      setLoading(false);
    }
  }, [fetchProjects, getTranslation]);

  // 删除项目
  const deleteProject = useCallback(async (id: number) => {
    setLoading(true);
    try {
      const response = await projectApi.deleteProject(id);
      if (response.code === 200) {
        message.success(getTranslation('项目删除成功', 'Project deleted successfully'));
        // 如果删除的是当前选中的项目，清除选择
        if (selectedProjectId === id) {
          setSelectedProjectId(null);
        }
        await fetchProjects();
      } else {
        message.error(response.message || getTranslation('删除项目失败', 'Failed to delete project'));
      }
    } catch (error) {
      console.error('删除项目出错:', error);
      message.error(getTranslation('删除项目出错', 'Error deleting project'));
    } finally {
      setLoading(false);
    }
  }, [fetchProjects, getTranslation, selectedProjectId]);

  // 处理项目选择
  const handleSelectProject = useCallback((projectId: number | null) => {
    setSelectedProjectId(projectId);
  }, []);

  // 初始加载
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    loading,
    selectedProjectId,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    handleSelectProject,
    getTranslation
  };
} 