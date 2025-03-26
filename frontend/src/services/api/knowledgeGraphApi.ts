import { api } from './core';
import { ConceptData, Relation } from './types';

// 创建关系的接口
interface CreateRelation {
  source_id: string;
  target_id: string;
  relation_type: string;
  description: string;
}

// 知识图谱相关API
export const knowledgeGraphApi = {
  getGraph: () => 
    api.get('/api/graph/knowledge-graph'),
    
  getConcepts: () => 
    api.get('/api/graph/concepts/'),
    
  getConceptDetail: (id: number) =>
    api.get(`/api/graph/concept/${id}`),
    
  createConcept: (data: ConceptData) => 
    api.post('/api/graph/concepts/', data),
    
  updateConcept: (id: number, data: ConceptData) =>
    api.put(`/api/graph/concept/${id}`, data),
    
  deleteConcept: (id: number) =>
    api.delete(`/api/graph/concept/${id}`),
    
  createRelation: (data: CreateRelation) => 
    api.post('/api/graph/relations/', data),
    
  deleteRelation: (id: number) =>
    api.delete(`/api/graph/relation/${id}`),
    
  updateConceptWeight: (id: number, data: { weight: number }) => 
    api.put(`/api/graph/concepts/${id}/weight`, data),
    
  extractConcepts: (paperId: number) => 
    api.post(`/api/graph/extract-concepts/${paperId}`),
    
  batchExtractConcepts: (limit?: number) => 
    api.post(`/api/graph/batch-extract-concepts${limit ? `?limit=${limit}` : ''}`),
    
  calculatePaperSimilarity: (paperId: number, threshold: number = 0.3, limit: number = 10) => 
    api.post(`/api/graph/paper-similarity?paper_id=${paperId}&threshold=${threshold}&limit=${limit}`),
    
  calculateTwoPapersSimilarity: (paperId1: number, paperId2: number) => 
    api.post('/api/graph/two-papers-similarity', { 
      paper_id1: paperId1, 
      paper_id2: paperId2 
    }),
    
  getReadingPath: (conceptId: number) => 
    api.get(`/api/graph/reading-path/${conceptId}`),
    
  getConceptPapers: (conceptId: number) => 
    api.get(`/api/graph/concept-papers/${conceptId}`)
}; 