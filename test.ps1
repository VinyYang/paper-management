# 创建安装缺失依赖的脚本
$scriptContent = @'
# 安装缺失的PyPDF2依赖
Write-Host "安装缺失的PyPDF2依赖..." -ForegroundColor Green
ssh root@47.108.139.79 "cd /var/www/ds/backend && source venv/bin/activate && pip install PyPDF2"

# 重置服务失败计数
Write-Host "重置服务失败计数..." -ForegroundColor Yellow
ssh root@47.108.139.79 "systemctl reset-failed ds-backend"

# 重启后端服务
Write-Host "重启后端服务..." -ForegroundColor Green
ssh root@47.108.139.79 "systemctl restart ds-backend"

# 等待几秒让服务启动
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 检查服务状态
Write-Host "检查服务状态..." -ForegroundColor Green
ssh root@47.108.139.79 "systemctl status ds-backend --no-pager"

# 检查服务是否在运行
Write-Host "验证API是否可访问..." -ForegroundColor Green
ssh root@47.108.139.79 "curl -s http://localhost:8003/docs | head"

Write-Host "`n=============== 总结 ===============" -ForegroundColor Cyan
$status = ssh root@47.108.139.79 "systemctl is-active ds-backend || echo 'inactive'"
if ($status -like "*active*") {
    Write-Host "后端服务已成功启动！" -ForegroundColor Green
    Write-Host "`n现在可以通过以下地址访问应用：" -ForegroundColor Green
    Write-Host "- 通过IP访问: http://47.108.139.79" -ForegroundColor Yellow
    Write-Host "- API文档: http://47.108.139.79/docs" -ForegroundColor Yellow
} else {
    Write-Host "后端服务仍未启动，查看最新错误日志..." -ForegroundColor Red
    ssh root@47.108.139.79 "journalctl -u ds-backend -n 30"
}
'@

# 保存脚本
$scriptContent | Out-File -FilePath "install_pypdf2.ps1" -Encoding utf8

# 执行脚本
Write-Host "执行脚本安装PyPDF2..." -ForegroundColor Cyan
./install_pypdf2.ps1