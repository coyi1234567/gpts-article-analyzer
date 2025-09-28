# 超级阅读研究助手

专业的文章解读与核查助手，支持微信、小红书、知乎、微博等多平台内容分析，具备图文结合分析能力。

## 🚀 功能特性

- **多平台支持**: 微信公众平台、小红书、知乎、微博、今日头条等
- **图文结合分析**: 自动抓取文章图片，结合文字内容进行深度分析
- **图片代理服务**: 解决防盗链问题，支持直接显示原图
- **智能缓存**: 图片缓存7天，自动过期清理
- **结构化分析**: 按文章类型提供专业分析框架

## 📋 分析框架

1. **基础信息** - 标题、作者、平台、发布时间
2. **类型识别** - 自动判断文章类型（新闻/论文/科普/技术等）
3. **结构化分析** - 按类型提供专业分析
4. **图文结合分析** - 详细解读每张图片内容
5. **真伪核查** - 标记可信度等级
6. **综合评价** - 给出专业建议

## 🛠️ 技术架构

- **后端**: Flask + Python
- **抓取**: BeautifulSoup + Requests
- **图片处理**: 代理服务 + 缓存机制
- **部署**: 支持Vercel、Render、Hugging Face Spaces

## 📦 快速部署

### Vercel部署（推荐）

1. Fork本仓库到您的GitHub
2. 在Vercel中导入项目
3. 自动部署完成

### 其他平台

- **Render**: 使用`render.yaml`配置
- **Hugging Face Spaces**: 使用`Dockerfile`配置

## 🔧 配置说明

### 环境变量

```bash
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5001
```

### 图片缓存配置

```python
IMAGE_CACHE_DAYS = 7  # 图片缓存7天
IMAGE_CACHE_MAX_AGE = 604800  # 7天 = 604800秒
```

## 📡 API接口

### 提取文章内容

```http
POST /extract
Content-Type: application/json

{
  "url": "https://mp.weixin.qq.com/s/xxxx"
}
```

### 图片代理

```http
GET /image/{encoded_url}
```

### 健康检查

```http
GET /health
```

## 🤖 GPTs集成

1. 在ChatGPT中创建新的GPTs
2. 配置Actions，使用本服务的API
3. 设置Instructions为专业的文章分析框架
4. 开始使用智能文章解读功能

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！