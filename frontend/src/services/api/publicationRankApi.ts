import { api } from './core';
import axios from 'axios';

// EasyScholar API配置
const EASYSCHOLAR_SECRET_KEY = 'ca89f21c31e244dabcc339cd7d8919bf';
const EASYSCHOLAR_API_URL = 'https://www.easyscholar.cc/open/getPublicationRank';

// 期刊等级颜色配置
export const rankColors: {
  [key: number]: string;
  textColor: string;
  fontSize: string;
} = {
  1: '#ff4d4f', // 一区/顶刊 - 红色
  2: '#40a9ff', // 二区 - 蓝色
  3: '#faad14', // 三区 - 金黄色
  4: '#73d13d', // 四区 - 绿色
  5: '#b37feb', // 其他 - 紫色
  textColor: '#ffffff', // 白色文字以提高对比度
  fontSize: '13px'
};

// 期刊等级接口
export interface PublicationRank {
  customRank?: {
    rankInfo?: Array<{
      uuid: string;
      abbName: string;
      oneRankText?: string;
      twoRankText?: string;
      threeRankText?: string;
      fourRankText?: string;
      fiveRankText?: string;
    }>;
    rank?: string[];
  };
  officialRank?: {
    all?: Record<string, string>;
    select?: Record<string, string>;
  };
}

// 解析后的期刊等级结果
export interface RankResult {
  source: string;
  rank: string;
  type: 'official' | 'custom';
  level?: number; // 1-5 对应自定义等级
}

export const publicationRankApi = {
  // 查询期刊等级
  getPublicationRank: async (publicationName: string): Promise<RankResult[]> => {
    try {
      // 对期刊名进行编码，防止特殊字符影响请求
      const encodedName = encodeURIComponent(publicationName);
      const requestUrl = `${EASYSCHOLAR_API_URL}?secretKey=${EASYSCHOLAR_SECRET_KEY}&publicationName=${encodedName}`;
      
      const response = await axios.get(requestUrl);
      
      if (response.data.code !== 200) {
        console.error('期刊等级查询失败:', response.data.msg);
        throw new Error(response.data.msg);
      }
      
      const results: RankResult[] = [];
      const data: PublicationRank = response.data.data;
      
      // 处理官方数据集结果
      if (data.officialRank && data.officialRank.all) {
        for (const [key, value] of Object.entries(data.officialRank.all)) {
          results.push({
            source: key,
            rank: value,
            type: 'official'
          });
        }
      }
      
      // 处理自定义数据集结果
      if (data.customRank && data.customRank.rankInfo && data.customRank.rank) {
        const rankInfoMap = new Map();
        
        // 构建数据集映射
        data.customRank.rankInfo.forEach(info => {
          rankInfoMap.set(info.uuid, info);
        });
        
        // 处理每个自定义等级
        data.customRank.rank.forEach(rankStr => {
          const [uuid, rankLevel] = rankStr.split('&&&');
          const rankInfo = rankInfoMap.get(uuid);
          
          if (rankInfo) {
            const level = parseInt(rankLevel);
            let rankText = '';
            
            // 根据等级获取对应的等级文本
            switch (level) {
              case 1: rankText = rankInfo.oneRankText || ''; break;
              case 2: rankText = rankInfo.twoRankText || ''; break;
              case 3: rankText = rankInfo.threeRankText || ''; break;
              case 4: rankText = rankInfo.fourRankText || ''; break;
              case 5: rankText = rankInfo.fiveRankText || ''; break;
            }
            
            if (rankText) {
              results.push({
                source: rankInfo.abbName,
                rank: rankText,
                type: 'custom',
                level: level
              });
            }
          }
        });
      }
      
      return results;
    } catch (error) {
      console.error('获取期刊等级失败:', error);
      throw error;
    }
  }
}; 