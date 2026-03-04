# Railway 完整自动化设置脚本
# 用法: .\setup-railway.ps1

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  WeChat Summary App - Railway 自动化部署设置" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 检查 Railway CLI
Write-Host "📋 检查 Railway CLI..." -ForegroundColor Yellow
$railwayVersion = railway --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Railway CLI 未安装" -ForegroundColor Red
    Write-Host "运行: npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Railway CLI 已安装: $railwayVersion" -ForegroundColor Green

# 检查项目路径
Write-Host ""
Write-Host "📁 项目路径: $(Get-Location)" -ForegroundColor Cyan

# Railway 配置变量
$projectName = "wechat-summary-app"
$githubRepo = "gzq0207-cpu/wechat-summary-app"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "下一步: 在浏览器中授权 Railway" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "请运行以下命令进行交互式登录:" -ForegroundColor Cyan
Write-Host "  railway login" -ForegroundColor Green
Write-Host ""
Write-Host "这会打开浏览器，你需要:" -ForegroundColor Cyan
Write-Host "  1. 使用 GitHub 授权登录 Railway" -ForegroundColor White
Write-Host "  2. 点击 'Authorize' 按钮" -ForegroundColor White
Write-Host "  3. 授权后返回终端继续" -ForegroundColor White
Write-Host ""

$response = Read-Host "你已完成授权吗? (y/n)"
if ($response -ne "y") {
    Write-Host "请先运行 'railway login' 完成授权" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ 授权完成!" -ForegroundColor Green

# 初始化 Railway 项目
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "创建 Railway 项目..." -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

try {
    railway init --name $projectName 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  项目初始化提示: Railway 可能已有现有项目" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Railway 项目创建成功" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  项目初始化提示: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 显示项目信息
Write-Host ""
Write-Host "📊 当前 Railway 项目信息:" -ForegroundColor Cyan
railway status 2>&1

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "⚠️  重要: 手动步骤需要完成" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "请在 Railway Dashboard 完成以下操作:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  添加 PostgreSQL 数据库服务:" -ForegroundColor Green
Write-Host "   • 打开: https://railway.app/dashboard" -ForegroundColor White
Write-Host "   • 选择项目 $projectName" -ForegroundColor White
Write-Host "   • 点击 '+ New Service' → 'Database' → 'PostgreSQL'" -ForegroundColor White
Write-Host "   • 等待 PostgreSQL 创建完成 (2-3 分钟)" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  配置后端服务环境变量:" -ForegroundColor Green
Write-Host "   • 点击后端服务 (wechat-summary-app)" -ForegroundColor White
Write-Host "   • 切换到 'Variables' 选项卡" -ForegroundColor White
Write-Host "   • 添加以下变量:" -ForegroundColor White
Write-Host "     FASTAPI_ENV=production" -ForegroundColor Magenta
Write-Host "     SECRET_KEY=<生成随机32字符>" -ForegroundColor Magenta
Write-Host "     LLM_PROVIDER=baidu" -ForegroundColor Magenta
Write-Host "     BAIDU_API_KEY=<你的API密钥>" -ForegroundColor Magenta
Write-Host "     BAIDU_SECRET_KEY=<你的SECRET密钥>" -ForegroundColor Magenta
Write-Host "     SCHEDULE_TIMEZONE=Asia/Shanghai" -ForegroundColor Magenta
Write-Host "     CRAWL_SCHEDULE_HOUR=9" -ForegroundColor Magenta
Write-Host "     CRAWL_SCHEDULE_MINUTE=0" -ForegroundColor Magenta
Write-Host ""
Write-Host "3️⃣  部署:" -ForegroundColor Green
Write-Host "   • 推送代码到 GitHub (已完成)" -ForegroundColor White
Write-Host "   • Railway 会自动检测并开始部署" -ForegroundColor White
Write-Host "   • 查看部署日志: Deployments 标签" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📝 有用的命令:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看项目状态:" -ForegroundColor Green
Write-Host "  railway status" -ForegroundColor White
Write-Host ""
Write-Host "查看实时日志:" -ForegroundColor Green
Write-Host "  railway logs" -ForegroundColor White
Write-Host ""
Write-Host "打开 Railway Dashboard:" -ForegroundColor Green
Write-Host "  railway open" -ForegroundColor White
Write-Host ""
Write-Host "检查部署状态:" -ForegroundColor Green
Write-Host "  railway logs --follow" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ 设置脚本完成!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
