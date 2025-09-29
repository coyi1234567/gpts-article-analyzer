# 🍪 知乎Cookie获取指南

## 📋 概述

要成功抓取知乎内容，最有效的方法是使用真实的登录Cookie。本指南将教您如何获取这些Cookie。

## 🔧 获取步骤

### 1. 登录知乎
1. 打开浏览器，访问 [https://www.zhihu.com](https://www.zhihu.com)
2. 使用您的账号登录知乎

### 2. 打开开发者工具
1. 按 `F12` 或右键点击页面选择"检查"
2. 切换到 `Application` 或 `应用程序` 标签
3. 在左侧找到 `Cookies` 选项
4. 点击 `https://www.zhihu.com`

### 3. 复制关键Cookie
找到以下Cookie并复制它们的值：

#### 必需Cookie：
- `d_c0` - 设备标识符
- `z_c0` - 用户认证令牌
- `_zap` - 会话标识符
- `q_c1` - 查询标识符

#### 可选Cookie：
- `tgw_l7_route` - 路由信息
- `__zse_ck` - 安全检查
- `Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49` - 访问时间
- `Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49` - 最后访问时间

### 4. 配置Cookie
将获取的Cookie添加到 `config.py` 文件中：

```python
ZHIHU_REAL_COOKIES = {
    'd_c0': '您的d_c0值',
    'z_c0': '您的z_c0值',
    '_zap': '您的_zap值',
    'q_c1': '您的q_c1值',
    'tgw_l7_route': '您的tgw_l7_route值',
    '__zse_ck': '您的__zse_ck值',
    'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49': '您的Hm_lvt值',
    'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49': '您的Hm_lpvt值',
}
```

## ⚠️ 注意事项

### 安全提醒：
1. **不要分享Cookie** - 这些Cookie包含您的身份信息
2. **定期更新** - Cookie会过期，需要定期更新
3. **保护隐私** - 不要在公共场所或不安全的网络环境下操作

### 使用建议：
1. **测试Cookie** - 配置后先测试是否有效
2. **监控状态** - 如果抓取失败，可能是Cookie过期
3. **备份Cookie** - 保存有效的Cookie配置

## 🚀 测试方法

配置Cookie后，测试知乎抓取：

```bash
curl -X POST http://127.0.0.1:5001/extract \
  -H "Content-Type: application/json" \
  -d '{"url":"https://zhuanlan.zhihu.com/p/您的文章ID"}'
```

## 📊 预期效果

使用真实Cookie后，知乎抓取成功率应该显著提升：
- ✅ 绕过403错误
- ✅ 访问更多内容
- ✅ 减少反爬检测
- ✅ 提高抓取稳定性

## 🔄 维护建议

1. **定期检查** - 每周检查一次Cookie是否有效
2. **及时更新** - 发现失效时立即更新
3. **监控日志** - 关注抓取日志中的错误信息
4. **备份配置** - 保存有效的Cookie配置

---

**提示**: 如果您遇到任何问题，请检查Cookie格式是否正确，或者尝试重新获取Cookie。

