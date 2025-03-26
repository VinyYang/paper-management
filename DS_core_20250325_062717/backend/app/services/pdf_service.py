import PyPDF2
import re
from typing import Dict, Any, Optional
import os

class PDFService:
    def __init__(self):
        self.metadata_patterns = {
            'doi': r'10\.\d{4,9}/[-._;()/:\w]+',
            'authors': r'Authors?:\s*([^\n]+)',
            'abstract': r'Abstract\s*([^\n]+(?:\n[^\n]+)*)',
            'journal': r'Journal:\s*([^\n]+)',
            'date': r'Date:\s*([^\n]+)'
        }
    
    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        从PDF文件中提取元数据
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # 获取第一页文本
                first_page = reader.pages[0].extract_text()
                
                # 提取元数据
                metadata = {}
                for key, pattern in self.metadata_patterns.items():
                    match = re.search(pattern, first_page, re.IGNORECASE)
                    if match:
                        metadata[key] = match.group(1).strip()
                
                # 如果没有找到DOI，尝试从文件名提取
                if 'doi' not in metadata:
                    filename = os.path.basename(file_path)
                    doi_match = re.search(self.metadata_patterns['doi'], filename)
                    if doi_match:
                        metadata['doi'] = doi_match.group(0)
                
                # 如果没有找到标题，使用文件名（不含扩展名）
                if 'title' not in metadata:
                    metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
                
                return metadata
                
        except Exception as e:
            print(f"Error extracting metadata: {str(e)}")
            return None
    
    def extract_text(self, file_path: str) -> Optional[str]:
        """
        提取PDF文件的文本内容
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return None
    
    def extract_references(self, file_path: str) -> Optional[list]:
        """
        提取参考文献
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                references = []
                
                # 查找参考文献部分
                for page in reader.pages:
                    text = page.extract_text()
                    if "References" in text or "Bibliography" in text:
                        # 提取DOI
                        dois = re.findall(self.metadata_patterns['doi'], text)
                        references.extend(dois)
                
                return references
        except Exception as e:
            print(f"Error extracting references: {str(e)}")
            return None 