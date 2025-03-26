import { api } from './core';
import { Note } from './types';

// 笔记相关API
export const noteApi = {
  getNotes: () => 
    api.get('/api/notes'),
    
  getNote: (id: number) => 
    api.get(`/api/notes/${id}`),
    
  createNote: (data: Partial<Note>) => 
    api.post('/api/notes', data),
    
  updateNote: (id: number, data: Partial<Note>) => 
    api.put(`/api/notes/${id}`, data),
    
  deleteNote: (id: number) => 
    api.delete(`/api/notes/${id}`),
    
  // 论文相关的笔记
  getPaperNotes: (paperId: number) => 
    api.get(`/api/papers/${paperId}/notes`),
    
  createPaperNote: (paperId: number, data: Partial<Note>) =>
    api.post(`/api/papers/${paperId}/notes`, data),
    
  updatePaperNote: (paperId: number, noteId: number, data: Partial<Note>) =>
    api.put(`/api/papers/${paperId}/notes/${noteId}`, data),
    
  deletePaperNote: (paperId: number, noteId: number) =>
    api.delete(`/api/papers/${paperId}/notes/${noteId}`)
}; 