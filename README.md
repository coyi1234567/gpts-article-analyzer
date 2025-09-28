# 🤖 GPTs智能文章解读器

一个专门为GPTs设计的文章内容提取服务，能够抓取网页文章内容（包括文字和图片URL），为GPTs提供结构化的数据进行分析。

## ✨ 功能特点

- **📄 多平台支持**：支持微信文章、网页文章等各种链接
- **🖼️ 图片提取**：提取文章中的图片URL，供GPTs Vision分析
- **🔍 内容结构化**：提供标题、正文、作者、发布时间等结构化信息
- **⚡ 轻量级**：不需要OpenAI API Key，专门为GPTs设计
- **🌐 易于部署**：支持Railway、Render、Heroku等平台

## 🚀 快速部署

### 方案1：Railway（推荐）

1. **Fork这个项目**到您的GitHub账户
2. **访问** [Railway](https://railway.app) 并登录
3. **点击** "New Project" → "Deploy from GitHub repo"
4. **选择** 您的项目仓库
5. **等待** 自动部署完成
6. **获取** 部署地址（类似：`https://your-project.railway.app`）

### 方案2：Render

1. **访问** [Render](https://render.com) 并登录
2. **点击** "New" → "Web Service"
3. **连接** GitHub仓库
4. **设置**：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. **部署** 并获取地址

## 🤖 创建GPTs

### 1. 打开ChatGPT
访问 [ChatGPT](https://chat.openai.com) → "Explore" → "Create a GPT"

### 2. 配置基本信息
- **Name**: `智能文章解读器`
- **Description**: `一个能够解读各种网页文章（包括微信文章）的智能助手，支持图文内容分析`

### 3. 配置Instructions
```
你是一个专业的文章解读助手。当用户提供文章链接时，使用extract_article函数获取文章内容，然后进行深度分析。

请从以下角度进行分析：
- 内容质量评估
- 核心观点提炼
- 逻辑结构分析
- 图片内容解读（如果有图片）
- 写作技巧评价
- 传播价值判断
- 目标受众分析

请始终保持客观、专业的分析态度。
```

### 4. 配置Actions
**点击 "Create new action"**，在Schema中粘贴：

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "文章提取API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-deployed-url.railway.app",
      "description": "部署的API服务器"
    }
  ],
  "paths": {
    "/extract": {
      "post": {
        "summary": "提取文章内容",
        "operationId": "extractArticle",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "url": {
                    "type": "string",
                    "description": "要提取的文章链接"
                  }
                },
                "required": ["url"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "提取成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {"type": "boolean"},
                    "data": {
                      "type": "object",
                      "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "author": {"type": "string"},
                        "publish_time": {"type": "string"},
                        "summary": {"type": "string"},
                        "images": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                              "url": {"type": "string"},
                              "alt": {"type": "string"},
                              "title": {"type": "string"}
                            }
                          }
                        },
                        "tags": {"type": "array", "items": {"type": "string"}}
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Authentication**: 选择 "None"

### 5. 测试GPTs
发送测试消息：
```
请分析这篇文章：https://mp.weixin.qq.com/s/example
```

## 📱 使用方式

在ChatGPT中直接发送：
```
请分析这篇文章：[文章链接]
```

GPTs会：
1. 调用API提取文章内容
2. 分析文字内容
3. 查看图片内容（如果有）
4. 提供综合解读报告

## 🧪 API测试

### 健康检查
```bash
curl https://your-deployed-url.railway.app/health
```

### 提取文章
```bash
curl -X POST https://your-deployed-url.railway.app/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://mp.weixin.qq.com/s/example"}'
```

## 📁 项目结构

```
chatgpt_wechat/
├── app.py                 # 主应用程序
├── web_scraper.py        # 网页抓取器
├── config.py             # 配置文件
├── requirements.txt      # 依赖包
├── Procfile             # Heroku部署配置
├── railway.json         # Railway部署配置
├── 部署指南.md          # 详细部署说明
└── README.md            # 项目说明
```

## 🔧 本地开发

```bash
# 克隆项目
git clone <your-repo-url>
cd chatgpt_wechat

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

## 🎯 核心优势

- **无需API Key**：不需要OpenAI API Key，利用GPTs自身能力
- **轻量级设计**：只做内容提取，分析交给GPTs
- **易于部署**：支持多种免费部署平台
- **高度兼容**：支持各种网页格式和文章类型

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

🎉 **现在您就拥有了一个完整的智能文章解读器GPTs！**