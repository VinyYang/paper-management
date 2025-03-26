// 用户相关类型
export interface UserData {
  username?: string;
  email?: string;
  password?: string;
  bio?: string;
  avatar_url?: string;
}

// 论文相关类型
export interface PaperData {
  title: string;
  authors: string;
  year?: number;
  journal?: string;
  abstract?: string;
  doi?: string;
  keywords?: string[];
  project_id?: number | null;
}

// 完整论文类型
export interface Paper {
  id: number;
  title: string;
  authors: string;
  journal?: string;
  year?: number;
  doi?: string;
  abstract?: string;
  created_at?: string;
  updated_at?: string;
  user_id?: number;
  tags?: string[];
  citations?: number;
  project_id?: number;
}

// 笔记相关类型
export interface Note {
  id: number;
  content: string;
  page_number: number;
  paper_id: number;
  created_at: string;
  updated_at: string;
}

// 项目相关类型
export interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  paper_count: number;
}

// 项目创建参数
export interface ProjectCreateParams {
  name: string;
  description?: string;
}

// 搜索结果类型
export interface SearchResult {
  id: number;
  title: string;
  authors: string[];
  year?: number;
  journal?: string;
  abstract?: string;
  doi?: string;
  url?: string;
  source: string;
}

// 概念相关类型
export interface ConceptData {
  name: string;
  definition?: string;
  examples?: string[];
  related_concepts?: string[];
  tags?: string[];
}

// 关系类型
export interface Relation {
  id: number;
  source_id: number;
  target_id: number;
  relation_type: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

// 反馈类型
export interface Feedback {
  content: string;
  type: 'bug' | 'feature' | 'general';
  email?: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 排名信息类型
export interface PublicationRank {
  custom?: {
    rank?: string;
    percentile?: number;
    impact_factor?: number;
  };
  official?: {
    ccf?: string;
    jcr?: string;
    sci?: boolean;
    ei?: boolean;
    impact_factor?: number;
  };
} 