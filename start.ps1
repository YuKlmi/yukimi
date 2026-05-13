Write-Host "============================================" -ForegroundColor Cyan
Write-Host "         选课系统 - 一键启动" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 启动后端
Write-Host "[1/2] 启动后端服务器..." -ForegroundColor Yellow
$backendJob = Start-Job -Name "backend" -ScriptBlock {
    Set-Location $using:rootDir\backend
    python app.py
}

# 等后端启动
Start-Sleep -Seconds 3

# 启动前端
Write-Host "[2/2] 启动前端开发服务器..." -ForegroundColor Yellow
$frontendJob = Start-Job -Name "frontend" -ScriptBlock {
    Set-Location $using:rootDir\frontend
    npm run dev
}

Write-Host ""
Write-Host "后端地址: http://localhost:5000" -ForegroundColor Green
Write-Host "前端地址: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Gray

# 等待用户中断
try {
    while ($true) {
        Start-Sleep -Seconds 1
        # 显示后台任务状态
        $jobs = Get-Job
        foreach ($job in $jobs) {
            if ($job.State -eq "Failed") {
                Write-Host "[错误] $($job.Name) 已停止" -ForegroundColor Red
                Receive-Job $job
            }
        }
    }
} finally {
    Write-Host "正在停止所有服务..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "已停止" -ForegroundColor Green
}
