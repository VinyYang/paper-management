# fix_all.ps1

# 瀹氫箟鏈嶅姟鍣ㄤ俊鎭?
$SERVER="47.108.139.79"
$USER="root"
$PASS="Yhy13243546"

# 纭繚鍙互浣跨敤plink
if (-not (Get-Command plink -ErrorAction SilentlyContinue)) {
    Write-Host "plink鍛戒护涓嶅彲鐢紝灏濊瘯浣跨敤SSH..." -ForegroundColor Yellow
    
    # 1. 瀹夎email-validator搴?
    Write-Host "瀹夎email-validator..." -ForegroundColor Green
    ssh root@47.108.139.79 "cd /var/www/ds/backend && source venv/bin/activate && pip install email-validator pydantic[email]"
    
    # 2. 閲嶇疆澶辫触璁℃暟骞堕噸鍚悗绔湇鍔?
    Write-Host "閲嶅惎鍚庣鏈嶅姟..." -ForegroundColor Green
    ssh root@47.108.139.79 "systemctl reset-failed ds-backend && systemctl restart ds-backend"
    
    # 3. 閰嶇疆Nginx
    Write-Host "閰嶇疆Nginx..." -ForegroundColor Green
    ssh root@47.108.139.79 "cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/ds/frontend/dist;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8003;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /docs {
        proxy_pass http://localhost:8003/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /openapi.json {
        proxy_pass http://localhost:8003/openapi.json;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF"
    
    # 4. 娴嬭瘯骞堕噸鍚疦ginx
    Write-Host "閲嶅惎Nginx..." -ForegroundColor Green
    ssh root@47.108.139.79 "nginx -t && systemctl restart nginx"
    
    # 5. 妫€鏌ユ湇鍔＄姸鎬?
    Write-Host "妫€鏌ユ湇鍔＄姸鎬?.." -ForegroundColor Green
    ssh root@47.108.139.79 "systemctl status ds-backend --no-pager"
    ssh root@47.108.139.79 "systemctl status nginx --no-pager"
} else {
    # 浣跨敤plink鎵ц鐩稿悓鐨勫懡浠わ紙閬垮厤澶氭杈撳叆瀵嗙爜锛?
    # 1. 瀹夎email-validator搴?
    Write-Host "瀹夎email-validator..." -ForegroundColor Green
    echo y | plink -pw $PASS "$USER@$SERVER" "cd /var/www/ds/backend && source venv/bin/activate && pip install email-validator pydantic[email]"
    
    # 2. 閲嶇疆澶辫触璁℃暟骞堕噸鍚悗绔湇鍔?
    Write-Host "閲嶅惎鍚庣鏈嶅姟..." -ForegroundColor Green
    echo y | plink -pw $PASS "$USER@$SERVER" "systemctl reset-failed ds-backend && systemctl restart ds-backend"
    
    # 3. 閰嶇疆Nginx
    Write-Host "閰嶇疆Nginx..." -ForegroundColor Green
    echo y | plink -pw $PASS "$USER@$SERVER" "cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/ds/frontend/dist;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8003;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /docs {
        proxy_pass http://localhost:8003/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /openapi.json {
        proxy_pass http://localhost:8003/openapi.json;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF"
    
    # 4. 娴嬭瘯骞堕噸鍚疦ginx
    Write-Host "閲嶅惎Nginx..." -ForegroundColor Green
    echo y | plink -pw $PASS "$USER@$SERVER" "nginx -t && systemctl restart nginx"
    
    # 5. 妫€鏌ユ湇鍔＄姸鎬?
    Write-Host "妫€鏌ユ湇鍔＄姸鎬?.." -ForegroundColor Green
    echo y | plink -pw $PASS "$USER@$SERVER" "systemctl status ds-backend --no-pager"
    echo y | plink -pw $PASS "$USER@$SERVER" "systemctl status nginx --no-pager"
}

# 鎬荤粨
Write-Host "`n=============== 鎬荤粨 ===============" -ForegroundColor Cyan
Write-Host "1. 宸插畨瑁卐mail-validator搴? -ForegroundColor Green
Write-Host "2. 宸查噸鍚悗绔湇鍔? -ForegroundColor Green
Write-Host "3. 宸查厤缃苟閲嶅惎Nginx" -ForegroundColor Green
Write-Host "`n璇烽€氳繃浠ヤ笅鍦板潃璁块棶鎮ㄧ殑搴旂敤:" -ForegroundColor Cyan
Write-Host "- 鐩存帴IP璁块棶: http://47.108.139.79" -ForegroundColor Yellow
Write-Host "- 鍩熷悕璁块棶(瑙ｆ瀽鐢熸晥鍚?: http://vinyyang.online" -ForegroundColor Yellow
Write-Host "`n濡傞渶閰嶇疆HTTPS锛岃杩愯浠ヤ笅鍛戒护:" -ForegroundColor Cyan
Write-Host "ssh root@47.108.139.79 ""apt install -y certbot python3-certbot-nginx && certbot --nginx -d vinyyang.online -d www.vinyyang.online""" -ForegroundColor Yellow
