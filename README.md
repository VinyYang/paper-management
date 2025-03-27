# 数据结构课程设计：学术文献管理系统
![首页Home Page](https://github.com/user-attachments/assets/5d43ce4c-bf23-43fe-8984-32b1114f6ed8)
## 系统简介

这是一个基于 FastAPI 和 React 构建的学术文献管理系统，用于高效管理学术文献、笔记和知识图谱。系统支持文献导入、元数据提取、知识图谱构建、笔记管理等功能，为学术研究提供全方位支持。

## 系统架构

### 后端架构
- **Web框架**：FastAPI 0.100.0
- **数据库ORM**：SQLAlchemy 2.0.0
- **WSGI服务器**：Uvicorn 0.22.0
- **图形数据处理**：NetworkX 3.4.2
- **数据分析**：Pandas 2.2.3, NumPy 1.24.0
- **PDF处理**：PyMuPDF 1.25.4, PyPDF2 3.0.1
- **机器学习**：Scikit-learn 1.6.1

### 前端架构
- **核心框架**：React 18
- **开发语言**：TypeScript
- **UI组件库**：Ant Design
- **可视化**：D3.js/ECharts
- **路由管理**：React Router
- **状态管理**：React Context API

## 功能特点

- **文献管理**：支持PDF导入、DOI查询、元数据提取
- **知识图谱**：自动构建文献关系网络，可视化知识关联
- **笔记系统**：支持PDF标注、结构化笔记、思维导图
- **智能推荐**：基于内容的文献推荐，研究路径规划
- **Sci-Hub集成**：支持通过DOI快速获取文献
- **主题切换**：支持浅色/深色/跟随系统三种模式
- **多语言支持**：支持中文和英文界面切换

## 服务器要求与建议

### 硬件推荐配置
- **CPU**：2核及以上
- **内存**：
  - **最低配置**：2GB（构建过程较慢，约20-30分钟）
  - **推荐配置**：4GB（构建时间约5-10分钟，性价比较高）
  - **理想配置**：8GB（大型项目或多项目并行开发）
- **存储**：20GB及以上SSD存储

### 内存不足解决方案
```bash
# 添加4GB的SWAP空间以缓解内存压力
dd if=/dev/zero of=/swapfile bs=1M count=4096
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 设为开机自动挂载
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 查看SWAP状态
free -h
```

## 安装与部署

### 开发环境

#### 后端设置
```bash
# 克隆仓库
git clone https://github.com/VinyYang/paper-management.git
cd paper-management/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

#### 前端设置
```bash
cd ../frontend

# 安装依赖
npm install

# 创建环境变量文件（开发环境）
echo "REACT_APP_API_URL=http://localhost:8003" > .env

# 启动开发服务器
npm start
```

### 生产环境部署

#### 前端环境变量配置
```bash
# 进入前端目录
cd /var/www/vinyyang/frontend

# 创建开发环境变量文件（用于本地开发）
echo "REACT_APP_API_URL=http://localhost:8003" > .env

# 创建生产环境变量文件（用于构建和部署）
echo "REACT_APP_API_URL=http://服务器IP地址/api" > .env.production
# 例如：
echo "REACT_APP_API_URL=http://118.178.253.237/api" > .env.production
```

#### 后端部署
```bash
# 创建服务文件
cat > /etc/systemd/system/vinyyang.service << 'EOF'
[Unit]
Description=VinyYang后端服务
After=network.target

[Service]
User=root  # 根据实际情况可改为www-data等用户
WorkingDirectory=/var/www/vinyyang/backend
ExecStart=/var/www/vinyyang/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动并设置开机自启
systemctl daemon-reload
systemctl start vinyyang
systemctl enable vinyyang
```

#### 前端构建与部署

##### 构建前端（低内存服务器优化）
```bash
# 进入前端目录
cd /var/www/vinyyang/frontend

# 安装依赖（解决依赖冲突）
npm install --legacy-peer-deps

# 如果react-scripts找不到，单独安装
npm install react-scripts --save-dev --legacy-peer-deps

# 优化构建过程（限制Node内存使用）
NODE_OPTIONS="--max-old-space-size=1536" npm run build --legacy-peer-deps

# 如果上述命令失败，可尝试
npx react-scripts build
```

##### 配置Nginx
```bash
# 创建Nginx配置文件
cat > /etc/nginx/sites-available/vinyyang << 'EOF'
server {
    listen 80;
    server_name 118.178.253.237;  # 替换为您的域名或服务器IP
    root /var/www/vinyyang/frontend/build;  # 注意React默认构建到build目录
    
    # 前端路由配置
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8003;  # 确保端口与后端一致
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# 启用站点（创建符号链接）
ln -s /etc/nginx/sites-available/vinyyang /etc/nginx/sites-enabled/

# 检查Nginx配置是否有效
nginx -t

# 启用并重启Nginx
systemctl enable nginx
systemctl restart nginx
```

## 使用说明

1. 访问系统首页登录或注册账户
2. 通过DOI或上传PDF导入文献
3. 在文献详情页查看信息并添加笔记
4. 使用知识图谱功能探索文献间关系
5. 根据系统推荐发现相关研究
6. 在设置页面切换语言和主题

## 系统状态检查与维护

### 确认前后端运行状态

#### 检查后端服务状态
```bash
# 检查服务运行状态
systemctl status vinyyang

# 查看后端进程
ps aux | grep uvicorn

# 查看后端日志
journalctl -u vinyyang -f

# 测试后端API
curl http://localhost:8003/docs
```

#### 检查前端服务状态
```bash
# 检查Nginx状态
systemctl status nginx

# 检查Nginx配置
nginx -t

# 检查前端文件
ls -la /var/www/vinyyang/frontend/build
```

### 确认前后端端口对齐

#### 检查端口配置一致性
```bash
# 查看后端实际监听的端口
netstat -tulpn | grep uvicorn

# 查看Nginx配置中的代理端口
grep -r "proxy_pass" /etc/nginx/sites-available/

# 查看前端环境变量中的API地址
cat /var/www/vinyyang/frontend/.env.production
```

#### 解决端口不一致问题
```bash
# 1. 修改前端环境变量以匹配后端端口（推荐）
echo "REACT_APP_API_URL=http://服务器IP地址/api" > /var/www/vinyyang/frontend/.env.production

# 2. 或修改后端端口以匹配前端配置
# 编辑systemd服务文件并修改端口号
nano /etc/systemd/system/vinyyang.service
systemctl daemon-reload
systemctl restart vinyyang

# 3. 同时需要更新Nginx配置中的代理地址
nano /etc/nginx/sites-available/vinyyang
nginx -t && systemctl reload nginx
```

### 故障排查与常见问题解决

#### 访问相关问题
- **404错误**：检查Nginx配置中的root路径是否指向正确的前端构建目录（build或dist）
- **502错误**：检查后端服务是否正常运行，端口是否被占用或防火墙是否阻止
- **跨域问题**：检查Nginx配置中的CORS设置或后端的CORS中间件配置
- **空白页面**：查看浏览器控制台是否有JavaScript错误，可能是构建过程中出现问题

#### 依赖安装与构建问题
```bash
# 清理npm缓存解决依赖冲突
npm cache clean --force

# 处理依赖冲突
npm install --legacy-peer-deps

# 处理react-scripts找不到的问题
npm list react-scripts
npm install react-scripts --save-dev --legacy-peer-deps

# 构建内存不足问题
# 创建SWAP并限制Node内存使用
dd if=/dev/zero of=/swapfile bs=1M count=4096
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
NODE_OPTIONS="--max-old-space-size=1536" npm run build --legacy-peer-deps
```

### 完全重启与服务自动化

#### 一键重启脚本
```bash
# 创建一个重启脚本
cat > /root/restart_services.sh << 'EOF'
#!/bin/bash
echo "重启后端服务..."
systemctl restart vinyyang
echo "重启Nginx服务..."
systemctl restart nginx
echo "确认服务状态..."
echo "后端服务状态:"
systemctl status vinyyang | grep Active
echo "Nginx服务状态:"
systemctl status nginx | grep Active
echo "设置开机自启动..."
systemctl enable vinyyang
systemctl enable nginx
echo "完成!"
EOF

# 设置脚本执行权限
chmod +x /root/restart_services.sh

# 执行重启脚本
/root/restart_services.sh
```

#### 定期自动重启（可选）
```bash
# 添加定时任务，每周日凌晨3点重启服务
(crontab -l 2>/dev/null; echo "0 3 * * 0 /root/restart_services.sh >> /var/log/service_restart.log 2>&1") | crontab -

# 查看定时任务
crontab -l
```

## 开发注意事项

### 主题和国际化

- 主题切换通过React Context API实现
- 语言切换使用Ant Design的国际化功能
- 开发新组件时需适配两种主题和两种语言
- 使用CSS变量而非固定颜色值以支持主题切换
- 使用翻译函数而非硬编码文本以支持多语言

### 代码贡献

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加新特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT License

---

**项目状态**: 活跃开发中  
**最后更新**: 2025-03-27  
**运行环境**: Python 3.10+, Node.js 16+

## 其他系统图片展示
### 文献库Paperbase
![文献库Paperbase](https://github.com/user-attachments/assets/e401aa0b-003d-435f-8880-d2cd2b868dee)
### 知识图谱Knowledge-Graph
![知识图谱Knowledge-Graph](https://github.com/user-attachments/assets/c180759e-7c16-4a2f-a21f-6ab464c74082)
### 论文相似度分析Paper-Similarity-Measurement
![论文相似度分析Paper-Similarity-Measurement](https://github.com/user-attachments/assets/28028325-ce14-487c-88ce-9b601f1ce374)
### 论文推荐Paper-Recommendation
![论文推荐Paper-Recommendation](https://github.com/user-attachments/assets/92f8a443-818e-42b7-a98c-6dd6ff1a6223)
### 论文检索Paper-Searching
![论文检索Paper-Searching](https://github.com/user-attachments/assets/c5e98a08-fdb9-48b1-b5a3-2a445ef06588)
### 项目Project
![项目Project](https://github.com/user-attachments/assets/e8b643d9-4285-48e2-bffb-bcbbc1326214)
### 设置
![设置](https://github.com/user-attachments/assets/3d883f29-942d-48c8-bbec-85492914d72d)
### 模式与语言切换Mode-Language-Change
![模式与语言切换Mode-Language-Change](https://github.com/user-attachments/assets/28af03c3-58eb-4385-92e5-31e7dafa57f7)
