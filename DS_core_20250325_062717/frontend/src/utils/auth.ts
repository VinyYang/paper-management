// 用户令牌的存储键名
const TOKEN_KEY = 'user_token';
const USER_INFO_KEY = 'user_info';

// 获取存储的令牌
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

// 设置令牌到本地存储
export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

// 移除令牌
export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

// 检查用户是否已登录
export const isLoggedIn = (): boolean => {
  return !!getToken();
};

// 保存用户信息
export const setUserInfo = (userInfo: any): void => {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo));
};

// 获取用户信息
export const getUserInfo = (): any => {
  const userInfoStr = localStorage.getItem(USER_INFO_KEY);
  if (userInfoStr) {
    try {
      return JSON.parse(userInfoStr);
    } catch (e) {
      console.error('解析用户信息失败:', e);
      return null;
    }
  }
  return null;
};

// 移除用户信息
export const removeUserInfo = (): void => {
  localStorage.removeItem(USER_INFO_KEY);
};

// 完全登出，清除所有用户相关数据
export const logout = (): void => {
  removeToken();
  removeUserInfo();
};

// 检查令牌是否过期
export const isTokenExpired = (token: string): boolean => {
  if (!token) {
    return true;
  }
  
  try {
    // JWT格式：header.payload.signature
    const payload = token.split('.')[1];
    if (!payload) {
      return true;
    }
    
    // 解码payload（Base64）
    const decodedPayload = JSON.parse(atob(payload));
    const exp = decodedPayload.exp;
    
    // 检查是否有过期时间
    if (!exp) {
      return false;
    }
    
    // 检查当前时间是否已经超过过期时间
    return Date.now() >= exp * 1000;
  } catch (e) {
    console.error('解析令牌时出错:', e);
    return true;
  }
}; 