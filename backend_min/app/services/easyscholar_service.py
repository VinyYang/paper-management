import requests
import logging
import os
from typing import Optional, Dict, Any

class EasyScholarService:
    """EasyScholar期刊等级查询服务"""
    
    API_URL = "https://www.easyscholar.cc/open/getPublicationRank"
    
    def __init__(self):
        # 从环境变量获取密钥，如果没有则使用默认值
        self.SECRET_KEY = os.getenv("EASYSCHOLAR_API_KEY", "ca89f21c31e244dabcc339cd7d8919bf")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("EasyScholarService")
        
        # 添加简单的内存缓存
        self.cache = {}
        self.cache_timeout = 3600  # 缓存1小时
        
        # 记录缓存使用情况
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_publication_rank(self, publication_name: str) -> Optional[Dict[str, Any]]:
        """
        获取期刊等级信息
        :param publication_name: 期刊名称
        :return: 期刊等级信息
        """
        # 检查缓存
        import time
        current_time = time.time()
        cache_key = publication_name.lower().strip()
        
        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            # 如果缓存未过期，直接返回缓存数据
            if current_time - cache_time < self.cache_timeout:
                self.cache_hits += 1
                self.logger.info(f"缓存命中: {publication_name} (命中率: {self.cache_hits/(self.cache_hits+self.cache_misses):.2%})")
                return cache_data
        
        # 缓存未命中，执行API请求
        self.cache_misses += 1
        
        try:
            # 避免请求频率过高
            time.sleep(0.5)
            
            # 构建请求URL
            params = {
                "secretKey": self.SECRET_KEY,
                "publicationName": publication_name
            }
            
            self.logger.info(f"查询期刊: {publication_name}")
            
            # 设置超时
            timeout = 10  # 10秒超时
            
            # 发送请求
            response = self.session.get(self.API_URL, params=params, timeout=timeout)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if data.get("code") != 200:
                self.logger.error(f"查询失败: {data.get('msg')}")
                return None
                
            self.logger.info(f"查询成功: {publication_name}")
            
            # 更新缓存
            result_data = data.get("data")
            self.cache[cache_key] = (result_data, current_time)
            
            return result_data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"查询期刊等级超时: {publication_name}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求异常: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"查询期刊等级失败: {str(e)}")
            return None
    
    def format_rank_info(self, rank_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化期刊等级信息，提取重要分区信息
        :param rank_data: 原始等级数据
        :return: 格式化后的等级信息
        """
        if not rank_data:
            return {"error": "没有查询到期刊等级信息"}
        
        formatted_info = {
            "sci": self._get_nested_value(rank_data, ["officialRank", "all", "sci"]),
            "ssci": self._get_nested_value(rank_data, ["officialRank", "all", "ssci"]),
            "sciif": self._get_nested_value(rank_data, ["officialRank", "all", "sciif"]),
            "sciUp": self._get_nested_value(rank_data, ["officialRank", "all", "sciUp"]),
            "ruc": self._get_nested_value(rank_data, ["officialRank", "all", "ruc"]),
            "pku": self._get_nested_value(rank_data, ["officialRank", "all", "pku"]),
            "cssci": self._get_nested_value(rank_data, ["officialRank", "all", "cssci"]),
            "cscd": self._get_nested_value(rank_data, ["officialRank", "all", "cscd"]),
            "custom_ranks": []
        }
        
        # 提取自定义数据集中的等级信息
        custom_rank_info = rank_data.get("customRank", {})
        rank_info_list = custom_rank_info.get("rankInfo", [])
        rank_list = custom_rank_info.get("rank", [])
        
        if rank_info_list and rank_list:
            rank_info_dict = {item["uuid"]: item for item in rank_info_list}
            
            for rank_str in rank_list:
                try:
                    uuid, rank_index = rank_str.split("&&&")
                    rank_index = int(rank_index)
                    
                    if uuid in rank_info_dict:
                        rank_item = rank_info_dict[uuid]
                        abb_name = rank_item.get("abbName", "未知")
                        
                        rank_texts = [
                            rank_item.get("oneRankText"),
                            rank_item.get("twoRankText"),
                            rank_item.get("threeRankText"),
                            rank_item.get("fourRankText"),
                            rank_item.get("fiveRankText")
                        ]
                        
                        if 1 <= rank_index <= 5 and rank_index <= len(rank_texts) and rank_texts[rank_index-1]:
                            formatted_info["custom_ranks"].append({
                                "name": abb_name,
                                "rank": rank_texts[rank_index-1]
                            })
                except Exception as e:
                    self.logger.error(f"解析自定义等级信息失败: {str(e)}")
        
        # 清除空值
        return {k: v for k, v in formatted_info.items() if v or k == "custom_ranks"}
    
    def _get_nested_value(self, data: Dict[str, Any], keys: list) -> Any:
        """
        获取嵌套字典中的值
        :param data: 字典数据
        :param keys: 键路径
        :return: 值或None
        """
        current = data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current 