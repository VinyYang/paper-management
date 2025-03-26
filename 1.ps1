# deploy.ps1 - 部署脚本
$SERVER="47.108.139.79"
$USER="root"
$PASS="Yhy13243546"  # 密码已加入，但请注意保护此脚本文件安全
$BACKEND_PATH="/var/www/ds/backend"
$FRONTEND_PATH="/var/www/ds/frontend/dist"
$BACKUP_DATE = Get-Date -Format "yyyyMMdd_HHmmss"

# 构建前端
Write-Host "Building frontend..." -ForegroundColor Green
Set-Location -Path ".\frontend"
npm run build
Set-Location -Path ".."

# 在服务器上创建备份
Write-Host "Creating backup..." -ForegroundColor Green
echo y | plink -pw $PASS "$USER@$SERVER" "mkdir -p /var/www/ds/backups/${BACKUP_DATE}/backend /var/www/ds/backups/${BACKUP_DATE}/frontend"
echo y | plink -pw $PASS "$USER@$SERVER" "cp -r ${BACKEND_PATH}/app ${BACKEND_PATH}/run.py /var/www/ds/backups/${BACKUP_DATE}/backend/"
echo y | plink -pw $PASS "$USER@$SERVER" "cp -r ${FRONTEND_PATH}/* /var/www/ds/backups/${BACKUP_DATE}/frontend/"

# 记录最新备份版本
echo y | plink -pw $PASS "$USER@$SERVER" "echo ${BACKUP_DATE} > /var/www/ds/backups/latest.txt"

# 上传后端文件
Write-Host "Uploading backend files..." -ForegroundColor Green
echo y | pscp -pw $PASS "./backend/run.py" "$USER@$SERVER`:$BACKEND_PATH/"
echo y | pscp -r -pw $PASS "./backend/app" "$USER@$SERVER`:$BACKEND_PATH/"

# 如果有requirements.txt变更，也上传并安装
if (Test-Path "./backend/requirements.txt") {
    Write-Host "Updating dependencies..." -ForegroundColor Yellow
    echo y | pscp -pw $PASS "./backend/requirements.txt" "$USER@$SERVER`:$BACKEND_PATH/"
    echo y | plink -pw $PASS "$USER@$SERVER" "cd ${BACKEND_PATH} && source venv/bin/activate && pip install -r requirements.txt"
}

# 上传前端文件
Write-Host "Uploading frontend files..." -ForegroundColor Green
echo y | pscp -r -pw $PASS "./frontend/build/*" "$USER@$SERVER`:$FRONTEND_PATH/"

# 重启后端服务
Write-Host "Restarting backend service..." -ForegroundColor Green
echo y | plink -pw $PASS "$USER@$SERVER" "systemctl restart ds-backend"

# 验证部署
Write-Host "Verifying deployment..." -ForegroundColor Yellow
$status = echo y | plink -pw $PASS "$USER@$SERVER" "systemctl is-active ds-backend"
if ($status -like "*active*") {  # 使用like匹配，处理可能的额外输出
    Write-Host "Deployment successful! Backend service is running." -ForegroundColor Green
} else {
    Write-Host "Warning: Backend service may not have started properly. Status: $status" -ForegroundColor Red
    $rollback = Read-Host "Do you want to rollback to previous version? (y/n)"
    if ($rollback -eq "y") {
        Write-Host "Executing rollback..." -ForegroundColor Yellow
        echo y | plink -pw $PASS "$USER@$SERVER" "cp -r /var/www/ds/backups/${BACKUP_DATE}/backend/* ${BACKEND_PATH}/"
        echo y | plink -pw $PASS "$USER@$SERVER" "cp -r /var/www/ds/backups/${BACKUP_DATE}/frontend/* ${FRONTEND_PATH}/"
        echo y | plink -pw $PASS "$USER@$SERVER" "systemctl restart ds-backend"
        Write-Host "Rollback completed" -ForegroundColor Green
    }
}

Write-Host "Deployment process completed" -ForegroundColor Green