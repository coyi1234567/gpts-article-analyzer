#!/bin/bash

echo "🚀 GPTs文章提取器一键部署脚本"
echo "=================================="

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 部署选项："
echo "1. Railway (推荐，免费)"
echo "2. Render (免费)"
echo "3. Heroku (免费额度有限)"
echo "4. 本地测试"
echo ""

read -p "请选择部署方式 (1-4): " choice

case $choice in
    1)
        echo "🚀 部署到Railway..."
        echo ""
        echo "📝 请按照以下步骤操作："
        echo "1. 访问 https://railway.app"
        echo "2. 使用GitHub账号登录"
        echo "3. 点击 'New Project'"
        echo "4. 选择 'Deploy from GitHub repo'"
        echo "5. 选择您的项目仓库"
        echo "6. Railway会自动检测并部署"
        echo ""
        echo "⏳ 等待部署完成后，您会得到一个公网地址"
        echo "📋 然后按照 部署指南.md 创建GPTs"
        ;;
    2)
        echo "🚀 部署到Render..."
        echo ""
        echo "📝 请按照以下步骤操作："
        echo "1. 访问 https://render.com"
        echo "2. 使用GitHub账号登录"
        echo "3. 点击 'New' → 'Web Service'"
        echo "4. 连接GitHub仓库"
        echo "5. 设置："
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python app.py"
        echo "6. 点击 'Create Web Service'"
        echo ""
        echo "⏳ 等待部署完成后，您会得到一个公网地址"
        echo "📋 然后按照 部署指南.md 创建GPTs"
        ;;
    3)
        echo "🚀 部署到Heroku..."
        echo ""
        echo "📝 请按照以下步骤操作："
        echo "1. 安装Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
        echo "2. 运行: heroku login"
        echo "3. 运行: heroku create your-app-name"
        echo "4. 运行: git push heroku main"
        echo ""
        echo "⏳ 等待部署完成后，您会得到一个公网地址"
        echo "📋 然后按照 部署指南.md 创建GPTs"
        ;;
    4)
        echo "🧪 本地测试..."
        echo ""
        echo "启动本地服务器..."
        source venv/bin/activate && python app.py
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 部署完成！"
echo "📖 详细说明请查看 部署指南.md"
echo "🤖 创建GPTs的步骤也在部署指南中"
