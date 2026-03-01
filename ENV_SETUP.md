# 环境变量配置说明

## 创建 .env 文件

在项目根目录下创建 `.env` 文件，并添加以下内容：

```
DASHSCOPE_API_KEY=your_api_key_here
```

## 获取阿里云百炼API密钥

1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
2. 登录您的账号
3. 进入API密钥管理页面
4. 创建或复制您的API密钥
5. 将密钥填入 `.env` 文件中的 `DASHSCOPE_API_KEY`

## 注意事项

- `.env` 文件已添加到 `.gitignore`，不会被提交到代码仓库
- 请妥善保管您的API密钥，不要泄露给他人
- 如果API密钥泄露，请及时在阿里云控制台重新生成
