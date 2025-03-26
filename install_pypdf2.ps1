# 瀹夎缂哄け鐨凱yPDF2渚濊禆
Write-Host "瀹夎缂哄け鐨凱yPDF2渚濊禆..." -ForegroundColor Green
ssh root@47.108.139.79 "cd /var/www/ds/backend && source venv/bin/activate && pip install PyPDF2"

# 閲嶇疆鏈嶅姟澶辫触璁℃暟
Write-Host "閲嶇疆鏈嶅姟澶辫触璁℃暟..." -ForegroundColor Yellow
ssh root@47.108.139.79 "systemctl reset-failed ds-backend"

# 閲嶅惎鍚庣鏈嶅姟
Write-Host "閲嶅惎鍚庣鏈嶅姟..." -ForegroundColor Green
ssh root@47.108.139.79 "systemctl restart ds-backend"

# 绛夊緟鍑犵璁╂湇鍔″惎鍔?
Write-Host "绛夊緟鏈嶅姟鍚姩..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 妫€鏌ユ湇鍔＄姸鎬?
Write-Host "妫€鏌ユ湇鍔＄姸鎬?.." -ForegroundColor Green
ssh root@47.108.139.79 "systemctl status ds-backend --no-pager"

# 妫€鏌ユ湇鍔℃槸鍚﹀湪杩愯
Write-Host "楠岃瘉API鏄惁鍙闂?.." -ForegroundColor Green
ssh root@47.108.139.79 "curl -s http://localhost:8003/docs | head"

Write-Host "`n=============== 鎬荤粨 ===============" -ForegroundColor Cyan
$status = ssh root@47.108.139.79 "systemctl is-active ds-backend || echo 'inactive'"
if ($status -like "*active*") {
    Write-Host "鍚庣鏈嶅姟宸叉垚鍔熷惎鍔紒" -ForegroundColor Green
    Write-Host "`n鐜板湪鍙互閫氳繃浠ヤ笅鍦板潃璁块棶搴旂敤锛? -ForegroundColor Green
    Write-Host "- 閫氳繃IP璁块棶: http://47.108.139.79" -ForegroundColor Yellow
    Write-Host "- API鏂囨。: http://47.108.139.79/docs" -ForegroundColor Yellow
} else {
    Write-Host "鍚庣鏈嶅姟浠嶆湭鍚姩锛屾煡鐪嬫渶鏂伴敊璇棩蹇?.." -ForegroundColor Red
    ssh root@47.108.139.79 "journalctl -u ds-backend -n 30"
}
