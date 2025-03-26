# API测试总结

## 重要发现

1. 认证Token获取
   - 正确的路由: `/api/users/token`
   - 请求方法: POST
   - Content-Type: `application/x-www-form-urlencoded`
   - 参数: `username` 和 `password`

2. 论文创建
   - 正确的路由: `/api/papers/` (注意末尾的斜杠很重要)
   - 请求方法: POST
   - Header需要: 
     - `Authorization: Bearer {token}`
     - `Content-Type: application/json`
   - 数据格式: JSON包含title, authors, journal, year, doi, abstract和tags等字段

## 测试步骤

1. 首先确保管理员用户存在，可运行 `ensure_admin.py` 脚本重置密码
2. 获取认证令牌
3. 使用令牌创建论文

## 测试工具

- `test_paper_api.py`: Python脚本测试论文创建API
- `check_api.py`: 检查所有API端点
- `check_routes.py`: 检查已注册的路由
- `check_service.py`: 检查服务是否正常运行
- `curl_test.bat`: 批处理脚本测试API (Windows)
- `curl_test.ps1`: PowerShell脚本测试API (Windows)

## 端口注意事项

当使用 `run.py` 启动服务时，需要指定端口:
```
python run.py --port 8002
```

## 常见问题

1. "Method Not Allowed" 错误:
   - 检查URL末尾是否有斜杠 `/`
   - 检查是否使用了正确的HTTP方法(GET/POST)

2. 认证失败:
   - 运行 `ensure_admin.py` 确保管理员账户正常
   - 检查用户名和密码是否正确

3. 服务无法启动:
   - 检查端口是否已被占用
   - 使用不同端口启动服务 