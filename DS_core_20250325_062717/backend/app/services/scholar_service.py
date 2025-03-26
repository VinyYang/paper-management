import aiohttp
import logging
import random
import asyncio
from typing import Optional, List, Dict, Any

class GoogleScholarService:
    """谷歌学术服务"""
    
    # 谷歌学术镜像站点 - 更新为更可能可用的镜像站
    MIRROR_SITES = [
        'https://sc.panda321.com/scholar',
        'https://xueshu.lanfanshu.cn/scholar',  
        'https://scholar.lanfanshu.cn/scholar',
        'https://scholar.scqylaw.com/scholar',
        'https://xueshu.sslchina.cn',
        'https://a.glgoo.top/scholar',
        'https://scholar.chongbuluo.com',
        'https://xueshu.cat-assets.workers.dev/scholar'
    ]
    
    # 上次检查时间和可用域名列表
    last_check_time = 0
    verified_sites = []
    check_interval = 1800  # 每30分钟检查一次可用性
    request_timeout = 10   # 每个请求10秒超时
    
    def __init__(self):
        """初始化日志和会话"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("GoogleScholarService")
    
    async def _verify_domains(self) -> List[str]:
        """验证哪些镜像站点可用"""
        current_time = asyncio.get_event_loop().time()
        
        # 如果验证过的域名列表不为空，且距离上次检查时间不超过检查间隔，直接返回缓存的结果
        if (self.verified_sites and 
            (current_time - self.last_check_time) < self.check_interval):
            return self.verified_sites
            
        self.logger.info("验证谷歌学术镜像站点可用性")
        available_sites = []
        
        # 创建异步会话
        async with aiohttp.ClientSession() as session:
            # 随机验证顺序，避免总是请求同一个站点
            sites_to_check = random.sample(self.MIRROR_SITES, len(self.MIRROR_SITES))
            
            # 创建一个任务列表进行并发检查
            tasks = []
            for site in sites_to_check:
                task = self._check_site_availability(session, site)
                tasks.append(task)
            
            # 等待任务完成
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for site, result in zip(sites_to_check, results):
                    # 忽略异常，只处理成功的结果
                    if isinstance(result, bool) and result:
                        available_sites.append(site)
                        # 找到3个可用站点后停止检查，以加快速度
                        if len(available_sites) >= 3:
                            break
            except Exception as e:
                self.logger.error(f"验证域名时出错: {str(e)}")
        
        # 如果没有可用站点，使用原始列表（假设暂时无法连接）
        if not available_sites:
            self.logger.warning("没有可用的镜像站点，使用原始列表")
            available_sites = self.MIRROR_SITES[:3]  # 使用前3个作为默认
        
        # 更新验证结果和时间
        self.verified_sites = available_sites
        self.last_check_time = current_time
        
        return available_sites
    
    async def _check_site_availability(self, session: aiohttp.ClientSession, site: str) -> bool:
        """检查单个站点是否可用"""
        try:
            # 构造一个简单查询URL
            test_url = f"{site}?q=test&as_ylo=2023"
            
            # 设置超时和请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            # 设置超时
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            
            async with session.get(test_url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    # 检查内容是否包含典型的谷歌学术页面特征
                    if 'gs_r' in html or 'gs_ri' in html:
                        self.logger.info(f"镜像站点可用: {site}")
                        return True
                    else:
                        self.logger.warning(f"镜像站点响应不包含谷歌学术特征: {site}")
                else:
                    self.logger.warning(f"镜像站点响应非200: {site}, 状态码: {response.status}")
        
        except asyncio.TimeoutError:
            self.logger.warning(f"镜像站点请求超时: {site}")
        except Exception as e:
            self.logger.warning(f"镜像站点检查失败: {site}, 错误: {str(e)}")
        
        return False
    
    async def search(self, query: str) -> Dict[str, Any]:
        """搜索谷歌学术并返回包含更多信息的结果"""
        # 验证可用的镜像站点
        available_sites = await self._verify_domains()
        
        # 对查询进行编码
        encoded_query = query.replace(' ', '+')
        
        # 设置响应数据结构
        result = {
            "success": False,
            "html": None,
            "url": None,
            "source": None,
            "originalTitle": query,
            "originalAuthor": "",
            "error": None
        }
        
        # 尝试每个可用的镜像站点
        for site in available_sites:
            try:
                # 构造URL
                search_url = f"{site}?q={encoded_query}&hl=zh-CN&as_sdt=0,5"
                
                # 设置请求头，模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Referer': 'https://scholar.google.com/'
                }
                
                self.logger.info(f"尝试从镜像站点搜索: {site}")
                
                # 创建会话并发送请求
                timeout = aiohttp.ClientTimeout(total=self.request_timeout)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(search_url, headers=headers) as response:
                        if response.status == 200:
                            # 读取HTML内容
                            html_content = await response.text()
                            
                            # 检查内容是否为谷歌学术页面（防止被重定向到登录页面等）
                            if 'gs_r' in html_content or 'gs_ri' in html_content:
                                self.logger.info(f"成功从镜像站点获取搜索结果: {site}")
                                
                                # 设置返回结果
                                result["success"] = True
                                result["html"] = html_content
                                result["url"] = search_url
                                result["source"] = site
                                
                                return result
                            else:
                                self.logger.warning(f"从镜像站点获取的内容不是谷歌学术页面: {site}")
                        else:
                            self.logger.warning(f"从镜像站点获取搜索结果失败, 状态码: {response.status}")
            
            except asyncio.TimeoutError:
                self.logger.error(f"从镜像站点搜索超时: {site}")
            except Exception as e:
                self.logger.error(f"从镜像站点搜索失败: {site}, 错误: {str(e)}")
        
        # 所有镜像站点都失败
        self.logger.error("所有镜像站点都无法获取搜索结果")
        result["error"] = "无法获取搜索结果，所有镜像站点都不可用"
        return result 