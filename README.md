# 🤖 超级阅读研究助手 - GPTs版本

一个专门为GPTs设计的智能文章解读器，支持微信、小红书、知乎、微博等多平台文章内容提取和图文分析。

## ✨ 功能特点

- 🚀 **多平台支持**：支持微信公众平台、小红书、知乎、微博、今日头条等主流平台
- 🖼️ **图文结合分析**：不仅提取文字内容，还能获取所有图片并生成代理链接
- 🔍 **智能图片过滤**：自动过滤装饰性图片，保留有价值的内容图片
- 🌐 **图片代理服务**：提供图片代理接口，绕过防盗链限制
- 📱 **GPTs集成**：专为GPTs设计，无需API密钥，直接使用GPTs的Vision功能
- ⚡ **高性能**：支持并发处理，响应速度快
- 📝 **小字总结**：每张图片下方都有简洁的总结说明

## 🏗️ 技术架构

- **后端**：Flask + Python
- **网页抓取**：BeautifulSoup + requests
- **图片处理**：Pillow + 代理服务
- **部署**：支持Vercel、Render、Railway等多种平台

## 🚀 快速开始

### 1. 本地开发

```bash
# 克隆项目
git clone https://github.com/coyi1234567/gpts-article-analyzer.git
cd gpts-article-analyzer

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

### 2. 部署到云平台

#### Vercel部署（推荐）

1. Fork本项目到你的GitHub
2. 在Vercel中导入项目
3. 自动部署完成

#### Railway部署

1. 在Railway中创建新项目
2. 连接GitHub仓库
3. 自动部署完成

#### Render部署

1. 在Render中创建Web Service
2. 连接GitHub仓库
3. 设置构建命令：`pip install -r requirements.txt`
4. 设置启动命令：`python app.py`

## 📡 API接口

### 提取文章内容

```http
POST /extract
Content-Type: application/json

{
  "url": "https://mp.weixin.qq.com/s/example"
}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "title": "文章标题",
    "content": "文章内容...",
    "author": "作者",
    "publish_time": "发布时间",
    "summary": "文章摘要",
    "images": [
      {
        "original_url": "原始图片链接",
        "proxy_url": "代理图片链接",
        "alt": "图片描述",
        "title": "图片标题",
        "index": 1,
        "description": "图片1 - 描述"
      }
    ],
    "tags": ["标签1", "标签2"]
  }
}
```

### 图片代理接口

```http
GET /image/{encoded_url}
```

## 🤖 GPTs配置

### 1. 创建GPTs

1. 打开ChatGPT，点击"Explore GPTs"
2. 点击"Create a GPT"
3. 选择"Configure"标签

### 2. 配置基本信息

- **Name**: 超级阅读研究助手
- **Description**: 专业的文章解读与核查助手，支持微信、小红书、知乎、微博等多平台内容分析，具备图文结合分析能力

### 3. 配置Instructions

复制`gpts_template.json`中的`instructions`内容到GPTs的Instructions字段。

### 4. 配置Actions

1. 点击"Create new action"
2. 复制`gpts_template.json`中的`openapi_schema`内容
3. 将服务器URL替换为你的部署地址

### 5. 测试GPTs

提供文章链接，测试GPTs是否能正确提取和分析内容。

## 📁 项目结构

```
gpts-article-analyzer/
├── app.py                 # Flask应用主文件
├── web_scraper.py         # 网页抓取器
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── gpts_template.json     # GPTs配置模板
├── vercel.json           # Vercel部署配置
├── render.yaml           # Render部署配置
├── railway.json          # Railway部署配置
├── Dockerfile            # Docker配置
├── Procfile              # Heroku部署配置
└── README.md             # 项目说明
```

## 🎯 核心功能说明

### 图片分析功能

- **完整图片提取**：提取文章中的所有图片，包括封面图、配图、数据图表等
- **智能过滤**：自动过滤装饰性图片，保留有价值的内容图片
- **代理服务**：提供图片代理接口，绕过防盗链限制
- **小字总结**：每张图片下方都有简洁的总结说明

### 文章分析功能

- **多平台支持**：支持微信、小红书、知乎、微博等主流平台
- **结构化分析**：按照专业框架进行文章分析
- **真伪核查**：对关键论点进行真伪核查和谣言识别
- **综合评价**：提供文章价值评估和可信度评级

## 🔧 配置说明

### 环境变量

- `FLASK_ENV`: Flask环境（development/production）
- `FLASK_DEBUG`: 调试模式（True/False）
- `PORT`: 服务端口（默认5001）
- `USER_AGENT`: 用户代理字符串
- `TIMEOUT`: 请求超时时间（默认30秒）

### 图片缓存配置

- `IMAGE_CACHE_DAYS`: 图片缓存天数（默认7天）
- `IMAGE_CACHE_MAX_AGE`: 图片缓存最大年龄（默认604800秒）

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 📞 联系方式

如有问题或建议，请提交Issue或联系开发者。

---

**注意**：本项目专为GPTs设计，无需OpenAI API密钥，直接使用GPTs的Vision功能进行图片分析。