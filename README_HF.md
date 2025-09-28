---
title: GPTs文章解读器
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# 🤖 GPTs智能文章解读器

一个专门为GPTs设计的文章内容提取服务，能够抓取网页文章内容（包括文字和图片URL），为GPTs提供结构化的数据进行分析。

## ✨ 功能特点

- **📄 多平台支持**：支持微信文章、网页文章等各种链接
- **🖼️ 图片提取**：提取文章中的图片URL，供GPTs Vision分析
- **🔍 内容结构化**：提供标题、正文、作者、发布时间等结构化信息
- **⚡ 轻量级**：不需要OpenAI API Key，专门为GPTs设计
- **🌐 易于部署**：支持多种免费部署平台

## 🚀 API接口

### 健康检查
```
GET /health
```

### 提取文章内容
```
POST /extract
Content-Type: application/json

{
  "url": "文章链接"
}
```

## 🎯 使用方式

在ChatGPT中创建GPTs，配置Actions调用此API，然后发送：
```
请分析这篇文章：[文章链接]
```

## 📱 支持的文章类型

- 微信文章
- 知乎文章
- 博客文章
- 新闻网站
- 其他网页文章

## 🔧 技术栈

- Python 3.9
- Flask
- BeautifulSoup4
- Requests
- Docker

## 📄 许可证

MIT License
