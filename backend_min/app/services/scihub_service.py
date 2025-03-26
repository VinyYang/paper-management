import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Any, List, Tuple
import logging
import time
import random

class SciHubService:
    # 官方最新链接列表（按推荐顺序排列）
    OFFICIAL_DOMAINS = [
        "https://www.sci-hub.wf/",
        "https://www.sci-hub.st/",
        "https://www.sci-hub.yt/",
        "https://www.sci-hub.se/",
        "https://www.sci-hub.ru/",
        "https://www.sci-hub.ee/",
        "https://www.sci-hub.ren/",
        "https://www.sci-hub.cat/",
        "https://www.pismin.com/",
        "https://www.wellesu.com/",
        "https://www.bothonce.com/"
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SciHubService")
        self.verified_domains = []  # 存储已验证可用的域名
        self.last_check_time = 0    # 上次检查域名的时间
        self.check_interval = 3600  # 每小时检查一次域名可用性
    
    def _verify_domains(self, force_check=False) -> List[str]:
        """验证域名是否可用，返回可用的域名列表"""
        current_time = time.time()
        
        # 如果已有验证过的域名且未到检查间隔，直接返回
        if self.verified_domains and not force_check and (current_time - self.last_check_time < self.check_interval):
            return self.verified_domains
        
        self.logger.info("开始验证SciHub域名可用性...")
        verified = []
        
        for domain in self.OFFICIAL_DOMAINS:
            try:
                # 使用5秒超时，避免长时间等待
                response = self.session.get(domain, timeout=5, allow_redirects=True)
                
                # 检查状态码和页面内容，确认是否是真正的SciHub页面
                if response.status_code == 200 and ('sci-hub' in response.text.lower() or 'doi' in response.text.lower()):
                    self.logger.info(f"域名 {domain} 可用")
                    verified.append(domain)
                    
                    # 只需要验证找到3个可用域名即可，避免过多请求
                    if len(verified) >= 3:
                        break
                else:
                    self.logger.warning(f"域名 {domain} 响应异常: {response.status_code}")
            except Exception as e:
                self.logger.warning(f"域名 {domain} 验证失败: {str(e)}")
            
            # 随机延迟，避免频繁请求
            time.sleep(random.uniform(0.5, 1.0))
        
        if not verified:
            self.logger.warning("所有SciHub域名验证失败，使用默认列表")
            verified = self.OFFICIAL_DOMAINS[:3]  # 使用前3个作为默认
        
        self.verified_domains = verified
        self.last_check_time = current_time
        
        return verified
    
    def get_paper_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """通过DOI获取论文信息"""
        # 确保获取最新验证的域名
        domains = self._verify_domains()
        
        for domain in domains:
            try:
                # 构建URL
                url = f"{domain}{doi}"
                self.logger.info(f"正在从SciHub获取论文: {url}")
                
                # 发送请求
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                # 检查响应内容类型是否为PDF
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' in content_type:
                    # 直接是PDF，无需解析
                    self.logger.info("SciHub直接返回了PDF文件")
                    return {
                        "title": f"Paper-{doi}",
                        "authors": "Unknown",
                        "abstract": "",
                        "pdf_url": url,
                        "doi": doi
                    }
                
                # 解析页面
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取信息
                title = self._extract_title(soup) or f"Paper-{doi}"
                authors = self._extract_authors(soup) or "Unknown"
                abstract = self._extract_abstract(soup) or ""
                pdf_url = self._extract_pdf_url(soup, response.url)
                
                if not pdf_url:
                    self.logger.warning(f"未能从 {domain} 提取PDF链接，尝试备用方式")
                    continue
                
                self.logger.info(f"从SciHub获取论文成功，PDF链接: {pdf_url}")
                
                return {
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "pdf_url": pdf_url,
                    "doi": doi
                }
                
            except Exception as e:
                self.logger.error(f"从 {domain} 获取论文失败: {str(e)}")
                # 继续尝试下一个域名
        
        self.logger.error(f"所有SciHub域名尝试失败，无法获取论文 DOI: {doi}")
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取论文标题"""
        title_elem = soup.find('h1', {'id': 'article-title'}) or soup.find('h1', {'class': 'title'})
        if title_elem:
            return title_elem.text.strip()
        
        # 尝试其他可能的标题元素
        title_elem = soup.find('div', {'id': 'citation'})
        if title_elem:
            match = re.search(r'"([^"]+)"', title_elem.text)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_authors(self, soup: BeautifulSoup) -> str:
        """提取作者信息"""
        authors_elem = soup.find('div', {'id': 'authors'}) or soup.find('div', {'class': 'authors'})
        return authors_elem.text.strip() if authors_elem else ""
    
    def _extract_abstract(self, soup: BeautifulSoup) -> str:
        """提取摘要"""
        abstract_elem = soup.find('div', {'id': 'abstract'}) or soup.find('div', {'class': 'abstract'})
        return abstract_elem.text.strip() if abstract_elem else ""
    
    def _extract_pdf_url(self, soup: BeautifulSoup, base_url: str) -> str:
        """提取PDF下载链接"""
        # 方法1：查找embed标签
        pdf_elem = soup.find('embed', {'id': 'pdf'})
        if pdf_elem and 'src' in pdf_elem.attrs:
            src = pdf_elem['src']
            # 如果是相对URL，转换为绝对URL
            if src.startswith('//'):
                return f"https:{src}"
            elif not src.startswith(('http://', 'https://')):
                return f"{base_url.rstrip('/')}/{src.lstrip('/')}"
            return src
        
        # 方法2：查找iframe
        iframe_elem = soup.find('iframe', {'id': 'pdf'})
        if iframe_elem and 'src' in iframe_elem.attrs:
            src = iframe_elem['src']
            if src.startswith('//'):
                return f"https:{src}"
            elif not src.startswith(('http://', 'https://')):
                return f"{base_url.rstrip('/')}/{src.lstrip('/')}"
            return src
        
        # 方法3：查找链接
        pdf_link = soup.find('a', href=lambda x: x and (x.endswith('.pdf') or 'pdf' in x))
        if pdf_link:
            href = pdf_link['href']
            if href.startswith('//'):
                return f"https:{href}"
            elif not href.startswith(('http://', 'https://')):
                return f"{base_url.rstrip('/')}/{href.lstrip('/')}"
            return href
        
        return ""
    
    def get_available_domains(self) -> List[str]:
        """获取当前可用的SciHub域名列表"""
        return self._verify_domains()
    
    def download_pdf(self, pdf_url: str) -> Optional[bytes]:
        """
        下载PDF文件
        """
        try:
            self.logger.info(f"开始下载PDF: {pdf_url}")
            # 设置较长的超时时间
            response = self.session.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # 验证是否为PDF文件
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' not in content_type and not pdf_url.endswith('.pdf'):
                self.logger.warning(f"响应不是PDF文件: {content_type}")
                # 解析HTML页面查找PDF链接
                soup = BeautifulSoup(response.text, 'html.parser')
                new_pdf_url = self._extract_pdf_url(soup, pdf_url)
                
                if new_pdf_url:
                    self.logger.info(f"找到新的PDF链接: {new_pdf_url}")
                    return self.download_pdf(new_pdf_url)
                else:
                    self.logger.error("无法找到PDF链接")
                    return None
            
            self.logger.info(f"PDF下载成功，大小: {len(response.content)} 字节")
            return response.content
        except Exception as e:
            self.logger.error(f"下载PDF失败: {str(e)}")
            return None
    
    async def download_pdf_async(self, pdf_url: str) -> Optional[bytes]:
        """
        异步下载PDF文件
        """
        try:
            self.logger.info(f"开始异步下载PDF: {pdf_url}")
            
            # 使用异步库下载
            import aiohttp
            
            # 设置超时
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(pdf_url) as response:
                    if response.status != 200:
                        self.logger.error(f"PDF下载失败，状态码: {response.status}")
                        return None
                    
                    # 验证是否为PDF文件
                    content_type = response.headers.get('Content-Type', '')
                    content = await response.read()
                    
                    if 'application/pdf' not in content_type and not pdf_url.endswith('.pdf'):
                        # 如果响应不是PDF，尝试查找PDF链接
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        new_pdf_url = self._extract_pdf_url(soup, pdf_url)
                        
                        if new_pdf_url:
                            self.logger.info(f"找到新的PDF链接: {new_pdf_url}")
                            return await self.download_pdf_async(new_pdf_url)
                        else:
                            self.logger.error("无法找到PDF链接")
                            return None
                    
                    self.logger.info(f"PDF异步下载成功，大小: {len(content)} 字节")
                    return content
                    
        except Exception as e:
            self.logger.error(f"异步下载PDF失败: {str(e)}")
            return None 