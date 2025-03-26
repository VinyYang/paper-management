import axios from 'axios';
import { message } from 'antd';
import axiosRetry from 'axios-retry';

// 创建一个axios实例
export const api = axios.create({
  baseURL: 'http://localhost:8003',
  timeout: 15000,  // 增加默认超时时间到15秒
  headers: {
    'Content-Type': 'application/json',
  }
});

// 配置重试机制
axiosRetry(api, { 
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error): boolean => {
    return !!(axiosRetry.isNetworkOrIdempotentRequestError(error) || 
           error.code === 'ECONNABORTED' || 
           (error.response && error.response.status >= 500));
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      // 确保 headers 存在
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    console.log('发送请求:', config.method?.toUpperCase(), config.url, config.headers);
    return config;
  },
  error => {
    console.error('请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { url, method } = response.config;
    console.log(`API响应成功: ${method?.toUpperCase()} ${url}`, response.data);
    return response;
  },
  error => {
    const { url, method } = error.config || {};
    console.error(`API请求错误: ${method?.toUpperCase()} ${url}`, {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status;
      const errorMessage = error.response.data?.detail || error.response.data?.message || '请求失败';
      
      if (status === 401) {
        // 未授权，清除token并跳转到首页
        console.warn('收到 401 未授权响应，清除 token 并跳转到首页');
        localStorage.removeItem('token');
        window.location.href = '/';
      } else if (status === 403) {
        message.error('没有权限访问此资源');
      } else if (status === 404) {
        message.error('请求的资源不存在');
      } else if (status === 409) {
        // 处理冲突错误，如DOI重复等
        message.error(errorMessage || '资源冲突，可能是数据已存在');
      } else if (status === 500) {
        message.error('服务器内部错误，请稍后重试');
      } else {
        message.error(errorMessage);
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      message.error('无法连接到服务器，请检查网络连接或服务器是否正常运行');
    } else {
      // 请求配置出错
      message.error('请求配置错误');
    }
    return Promise.reject(error);
  }
);

// 添加错误消息管理机制，防止短时间内显示相同错误
export const errorMessageManager = {
  messages: new Set<string>(),
  timeouts: new Map<string, NodeJS.Timeout>(),
  
  // 显示错误消息，避免重复
  showErrorOnce: (msg: string, duration: number = 3) => {
    // 如果相同消息已经在显示中，则不再显示
    if (errorMessageManager.messages.has(msg)) {
      return;
    }
    
    // 添加消息到集合中
    errorMessageManager.messages.add(msg);
    message.error(msg, duration);
    
    // 设置超时，从集合中移除消息
    const timeout = setTimeout(() => {
      errorMessageManager.messages.delete(msg);
      errorMessageManager.timeouts.delete(msg);
    }, duration * 1000);
    
    errorMessageManager.timeouts.set(msg, timeout);
  },
  
  // 显示提示消息，避免重复
  showInfoOnce: (msg: string, duration: number = 3) => {
    // 如果相同消息已经在显示中，则不再显示
    if (errorMessageManager.messages.has(msg)) {
      return;
    }
    
    // 添加消息到集合中
    errorMessageManager.messages.add(msg);
    message.info(msg, duration);
    
    // 设置超时，从集合中移除消息
    const timeout = setTimeout(() => {
      errorMessageManager.messages.delete(msg);
      errorMessageManager.timeouts.delete(msg);
    }, duration * 1000);
    
    errorMessageManager.timeouts.set(msg, timeout);
  },
  
  // 显示成功消息，避免重复
  showSuccessOnce: (msg: string, duration: number = 3) => {
    // 如果相同消息已经在显示中，则不再显示
    if (errorMessageManager.messages.has(msg)) {
      return;
    }
    
    // 添加消息到集合中
    errorMessageManager.messages.add(msg);
    message.success(msg, duration);
    
    // 设置超时，从集合中移除消息
    const timeout = setTimeout(() => {
      errorMessageManager.messages.delete(msg);
      errorMessageManager.timeouts.delete(msg);
    }, duration * 1000);
    
    errorMessageManager.timeouts.set(msg, timeout);
  },
  
  // 处理API请求错误，显示错误消息
  handleError: (error: any, defaultMessage: string) => {
    console.error('API错误:', error);
    let errorMsg = defaultMessage;
    
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message;
    } else if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail;
    } else if (error.message) {
      errorMsg = error.message;
    }
    
    errorMessageManager.showErrorOnce(errorMsg);
  },
  
  // 清除所有消息
  clearAll: () => {
    errorMessageManager.messages.clear();
    errorMessageManager.timeouts.forEach(timeout => clearTimeout(timeout));
    errorMessageManager.timeouts.clear();
  }
};

// 确保字符串不为undefined
export const ensureString = (value: string | undefined | null): string => {
  return value !== undefined && value !== null ? value : '';
}; 