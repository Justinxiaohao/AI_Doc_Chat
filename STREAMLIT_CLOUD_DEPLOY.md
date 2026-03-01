# Streamlit Cloud 部署指南

## 前置要求

1. GitHub账号
2. Streamlit Cloud账号（使用GitHub登录）
3. 阿里云百炼API密钥

## 部署步骤

### 1. 准备代码仓库

确保您的代码已推送到GitHub仓库，包含以下文件：
- `app.py` - 主程序
- `requirements.txt` - 依赖列表
- `.streamlit/config.toml` - Streamlit配置（可选）

### 2. 登录Streamlit Cloud

1. 访问 [https://share.streamlit.io/](https://share.streamlit.io/)
2. 点击 "Sign in" 使用GitHub账号登录
3. 授权Streamlit Cloud访问您的GitHub仓库

### 3. 创建新应用

1. 点击右上角的 "New app" 按钮
2. 填写应用信息：
   - **Repository**: 选择您的GitHub仓库
   - **Branch**: 选择主分支（通常是 `main` 或 `master`）
   - **Main file path**: 输入 `app.py`
   - **Python version**: 选择 3.10 或更高版本（推荐 3.10）

3. 点击 "Deploy!" 按钮

### 4. 配置环境变量（Secrets）

部署后，需要配置API密钥：

1. 在应用页面，点击右上角的 "⋮" 菜单
2. 选择 "Settings"
3. 在左侧菜单中找到 "Secrets"
4. 在Secrets编辑器中添加：

```toml
DASHSCOPE_API_KEY = "your_api_key_here"
```

5. 点击 "Save" 保存

### 5. 重新部署

配置Secrets后，应用会自动重新部署。等待部署完成即可使用。

## 应用管理

### 查看日志

在应用页面点击 "Manage app" → "Logs" 可以查看应用运行日志。

### 更新应用

每次您向GitHub仓库推送代码时，Streamlit Cloud会自动检测并重新部署应用。

### 删除应用

在应用设置中选择 "Delete app" 可以删除应用。

## 常见问题

### 1. 部署失败

- 检查 `requirements.txt` 中的依赖是否正确
- 查看日志中的错误信息
- 确保Python版本兼容

### 2. API密钥未生效

- 确认Secrets中已正确设置 `DASHSCOPE_API_KEY`
- 检查密钥是否正确（没有多余的空格）
- 重新部署应用

### 3. 应用运行缓慢

- Streamlit Cloud免费版有资源限制
- 考虑升级到付费版本
- 优化代码减少资源消耗

### 4. 文件上传限制

- Streamlit Cloud对文件大小有限制
- 建议上传的文件不超过200MB
- 大文件建议分批处理

## 注意事项

- Streamlit Cloud免费版有使用限制
- 应用在无活动时会休眠，首次访问需要几秒启动
- 确保不要将API密钥提交到GitHub仓库
- 使用 `.gitignore` 排除敏感文件

## 获取帮助

- Streamlit Cloud文档: [https://docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- Streamlit论坛: [https://discuss.streamlit.io/](https://discuss.streamlit.io/)
