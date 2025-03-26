# PDF加载问题修复方案

## 问题描述

在系统的PDF阅读功能中，即使PDF文件已成功上传到服务器，前端仍无法正常加载PDF文件，出现以下错误：

```
PDF加载失败: Failed to fetch. 请求URL: http://localhost:8000/api/papers/221/pdf
```

或

```
PDF加载失败: Unexpected server response (401) while retrieving PDF "http://localhost:8003/api/papers/1/pdf?t=1742794178205".
```

## 问题原因

1. 端口配置不一致：前端代码中硬编码使用了错误的服务器端口（8000），而实际后端服务运行在8003端口
2. 认证问题：PDF文件请求没有携带认证令牌（Bearer Token），导致服务器返回401未授权错误
3. 请求方式问题：直接在PDF查看器组件中使用URL，而没有通过已配置的API实例发送请求

## 解决方案

### 1. 修改前端代码，使用Blob方式加载PDF

在`PaperReader.tsx`文件中，添加以下代码替换原有的URL直接引用方式：

```typescript
const fetchPdf = async () => {
  setLoading(true);
  try {
    // 使用api发起请求，自动带上认证令牌
    const response = await api.get(`/api/papers/${id}/pdf`, {
      responseType: 'blob',
    });
    
    // 创建Blob URL
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const blobUrl = URL.createObjectURL(blob);
    
    setPdfUrl(blobUrl);
    setLoading(false);
  } catch (error) {
    console.error('加载PDF失败:', error);
    errorManager.showErrorOnce('PDF加载失败');
    setLoading(false);
  }
};
```

并在`useEffect`中调用此函数：

```typescript
useEffect(() => {
  if (id) {
    fetchPdf();
    fetchNotes();
  }
}, [id]);
```

### 2. 将直接使用的axios替换为配置好的api实例

将`PaperReader.tsx`中所有直接使用axios的地方改为使用已配置好认证的api实例：

```typescript
// 错误方式
import axios from 'axios';
const response = await axios.get(`http://localhost:8003/api/papers/${id}/notes`);

// 正确方式
import api from '../services/api';
const response = await api.get(`/api/papers/${id}/notes`);
```

### 3. 确保CORS配置正确

在后端的`config.py`文件中，确保允许的源包含前端应用实际使用的地址：

```python
ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://127.0.0.1:3000", "http://127.0.0.1:8000", "http://127.0.0.1:8001", "http://localhost:8003"]
```

## 实现原理

这种修复方案的原理是：

1. **使用API实例**：通过配置好的API实例发送请求，该实例已设置了请求拦截器，自动添加认证令牌
2. **Blob处理**：将服务器返回的二进制PDF数据转换为Blob对象，并创建本地Blob URL
3. **本地引用**：PDF查看器组件从本地Blob URL加载PDF，而不是直接从服务器URL加载

这种方式解决了认证问题，因为对服务器的请求携带了认证令牌，且避免了跨域问题，因为创建的是本地Blob URL。

## 注意事项

1. 确保在组件卸载时释放Blob URL以避免内存泄漏
2. 确保API实例中的baseURL与后端服务地址一致
3. 如果PDF较大，可能需要添加加载进度提示 