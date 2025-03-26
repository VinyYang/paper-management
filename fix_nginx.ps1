$nginxConfig = @"
server {
    listen 80;
    server_name _;

    root /var/www/ds/frontend/dist;
    index index.html;

    location / {
        try_files `$uri `$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8003/docs;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8003/openapi.json;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
    }
}
"@

# 使用plink将配置文件保存到服务器上的/tmp目录
$nginxConfig | Out-File -Encoding ASCII -FilePath nginx.conf

# 上传配置文件到服务器
echo y | pscp -pw "Yhy13243546" nginx.conf root@47.108.139.79:/tmp/nginx.conf

# 使用plink移动配置文件并重启Nginx
echo y | plink -pw "Yhy13243546" root@47.108.139.79 "mv /tmp/nginx.conf /etc/nginx/conf.d/default.conf && systemctl restart nginx"

# 删除本地临时文件
Remove-Item nginx.conf -Force 