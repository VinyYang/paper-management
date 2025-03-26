from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Dict
import httpx
import json
import re
from ..dependencies import get_current_user
from ..models import User

router = APIRouter()

# EasyScholar API 密钥
SECRET_KEY = "ca89f21c31e244dabcc339cd7d8919bf"
API_URL = "https://www.easyscholar.cc/open/getPublicationRank"

# DOI 到期刊名称的映射（可以不断扩充）
DOI_TO_JOURNAL_MAP: Dict[str, str] = {
    "10.1016/j.jss.2014.06.002": "Journal of Surgical Research",
    "10.1061/(asce)cp.1943-5487.0000706": "Journal of Computing in Civil Engineering"
}

def is_doi(query: str) -> bool:
    """判断查询字符串是否为DOI"""
    # 简单的DOI格式检查
    doi_pattern = r'10\.\d{4,}\/[-._;()/:a-zA-Z0-9]+'
    return bool(re.match(doi_pattern, query))

def get_journal_name_from_doi(doi: str) -> Optional[str]:
    """通过DOI获取期刊名称"""
    return DOI_TO_JOURNAL_MAP.get(doi)

@router.get("/{query}")
async def get_publication_rank(
    query: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    获取期刊等级信息，支持期刊名称或DOI
    """
    publication_name = query
    
    # 检查是否是DOI，如果是则尝试转换为期刊名称
    if is_doi(query):
        journal_name = get_journal_name_from_doi(query)
        if journal_name:
            publication_name = journal_name
        else:
            # 如果找不到对应的期刊名称，返回一个友好的错误
            return {
                "code": 404,
                "msg": "未能找到该DOI对应的期刊名称",
                "data": {
                    "doi": query,
                    "note": "此DOI未在系统中注册对应的期刊名称。请尝试直接搜索期刊名称。"
                }
            }
    
    try:
        # 构建请求URL
        url = f"{API_URL}?secretKey={SECRET_KEY}&publicationName={publication_name}"
        
        # 发送请求到EasyScholar API
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # 如果响应状态码不是2xx，则抛出异常
            
            # 解析响应数据
            data = response.json()
            
            # 检查API响应状态
            if data["code"] != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"API错误: {data['msg']}"
                )
            
            # 处理返回的数据，提取出我们需要的分区信息
            api_data = data["data"]
            result = {
                "doi": query if is_doi(query) else None,
                "journal": publication_name
            }
            
            # 处理官方分区信息
            if "officialRank" in api_data and api_data["officialRank"]:
                official_rank = api_data["officialRank"]
                
                # 处理所有分区
                if "all" in official_rank:
                    for rank_type, rank_value in official_rank["all"].items():
                        result[rank_type] = rank_value
                
                # 处理选择的分区
                if "select" in official_rank:
                    for rank_type, rank_value in official_rank["select"].items():
                        if rank_type not in result:
                            result[rank_type] = rank_value
            
            # 处理自定义分区信息
            custom_ranks = []
            if "customRank" in api_data and api_data["customRank"]:
                custom_rank = api_data["customRank"]
                
                if "rankInfo" in custom_rank and "rank" in custom_rank:
                    rank_info = {item["uuid"]: item for item in custom_rank["rankInfo"]}
                    
                    for rank_str in custom_rank["rank"]:
                        parts = rank_str.split("&&&")
                        if len(parts) == 2:
                            uuid, rank_num = parts
                            rank_num = int(rank_num)
                            
                            if uuid in rank_info:
                                info = rank_info[uuid]
                                rank_text = None
                                
                                # 根据rank_num获取对应等级文本
                                if rank_num == 1 and "oneRankText" in info:
                                    rank_text = info["oneRankText"]
                                elif rank_num == 2 and "twoRankText" in info:
                                    rank_text = info["twoRankText"]
                                elif rank_num == 3 and "threeRankText" in info:
                                    rank_text = info["threeRankText"]
                                elif rank_num == 4 and "fourRankText" in info:
                                    rank_text = info["fourRankText"]
                                elif rank_num == 5 and "fiveRankText" in info:
                                    rank_text = info["fiveRankText"]
                                
                                if rank_text and "abbName" in info:
                                    custom_ranks.append({
                                        "name": info["abbName"],
                                        "rank": rank_text
                                    })
            
            if custom_ranks:
                result["custom_ranks"] = custom_ranks
            
            return result
    except httpx.RequestError as e:
        # 处理请求异常
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"请求EasyScholar API时出错: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        # 处理HTTP状态错误
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"EasyScholar API返回错误: {e.response.text}"
        )
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取期刊等级信息时出错: {str(e)}"
        ) 