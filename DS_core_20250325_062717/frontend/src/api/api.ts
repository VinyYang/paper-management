import axios from 'axios';
import { getToken } from '../utils/auth';

// 创建API实例
export const api = axios.create({
  baseURL: 'http://localhost:8003', // 根据部署环境可能需要修改
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 获取用户令牌并添加到请求头
    const token = getToken();
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 如果返回的是blob类型，直接返回
    if (response.config.responseType === 'blob') {
      return response;
    }
    
    // 处理普通JSON响应
    return response;
  },
  error => {
    // 处理请求错误
    if (error.response) {
      const { status, data } = error.response;
      
      // 处理401未授权错误
      if (status === 401) {
        console.log('用户未授权，请登录');
        // 可以在这里添加重定向到登录页面的逻辑
        // window.location.href = '/login';
      }
      
      // 处理403禁止访问错误
      if (status === 403) {
        console.log('禁止访问该资源');
      }
      
      // 处理404未找到资源错误
      if (status === 404) {
        console.log('资源不存在');
      }
      
      // 处理500服务器错误
      if (status === 500) {
        console.log('服务器错误');
      }
      
      // 如果后端返回了错误消息，使用后端的错误消息
      if (data && data.message) {
        return Promise.reject(new Error(data.message));
      }
    }
    
    // 处理请求取消的情况
    if (axios.isCancel(error)) {
      console.log('请求已取消:', error.message);
      return Promise.reject(new Error('请求已取消'));
    }
    
    // 处理网络错误
    if (error.message && error.message.includes('Network Error')) {
      console.log('网络错误，请检查您的网络连接');
      return Promise.reject(new Error('网络错误，请检查您的网络连接'));
    }
    
    // 处理超时错误
    if (error.message && error.message.includes('timeout')) {
      console.log('请求超时，请稍后重试');
      return Promise.reject(new Error('请求超时，请稍后重试'));
    }
    
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 用于取消请求的控制器映射
const controllers = new Map();

// 取消特定API请求的函数
export const cancelRequest = (key: string) => {
  if (controllers.has(key)) {
    controllers.get(key).abort();
    controllers.delete(key);
  }
};

// 取消所有API请求的函数
export const cancelAllRequests = () => {
  controllers.forEach(controller => {
    controller.abort();
  });
  controllers.clear();
};

// 创建可取消的请求函数
export const createCancellableRequest = (key: string) => {
  // 如果已存在同名的请求，先取消
  if (controllers.has(key)) {
    cancelRequest(key);
  }
  
  // 创建新的AbortController
  const controller = new AbortController();
  controllers.set(key, controller);
  
  return {
    signal: controller.signal,
    cancelRequest: () => cancelRequest(key),
  };
}; 