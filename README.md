# RAG文档问答系统

基于LangChain + 阿里云百炼平台 + ChromaDB + Streamlit构建的智能文档问答系统。

## 功能特性

- 📁 **文档上传**: 支持PDF和TXT文件上传
- ✂️ **智能切片**: 自动按1000字符切片，重叠200字符
- 🔍 **向量检索**: 使用阿里云百炼text-embedding-v3模型生成向量
- 💬 **智能问答**: 基于qwen-max模型生成回答
- 📎 **来源追踪**: 显示回答来源的具体文档和片段
- 💾 **对话历史**: 保存对话历史，支持清空

## 技术栈

- **LangChain**: 大语言模型应用框架
- **阿里云百炼**: Embedding和对话模型
- **ChromaDB**: 向量数据库
- **Streamlit**: Web界面框架

## 安装步骤

1. **克隆或下载项目**

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**

创建`.env`文件（参考`.env.example`），填入您的阿里云百炼API密钥：
```
DASHSCOPE_API_KEY=your_api_key_here
```

4. **运行应用**
```bash
streamlit run app.py
```

## 使用说明

1. 在左侧边栏上传PDF或TXT文件
2. 点击"处理文档"按钮，系统会自动：
   - 提取文档文本
   - 进行智能切片
   - 生成向量并存入ChromaDB
3. 在主界面输入问题，系统会：
   - 检索相关文档片段
   - 使用大模型生成回答
   - 显示回答来源
4. 可以查看对话历史，或清空重新开始

## 配置说明

### 模型配置

- **Embedding模型**: text-embedding-v3
- **对话模型**: qwen-max（可在代码中改为qwen-turbo）
- **API Base**: https://dashscope.aliyuncs.com/compatible-mode/v1

### 切片参数

- **chunk_size**: 1000字符
- **chunk_overlap**: 200字符

可在`app.py`中的`split_documents`函数中修改。

## 部署到Streamlit Cloud

### 步骤

1. **将代码推送到GitHub仓库**
   - 确保代码已提交到GitHub

2. **访问Streamlit Cloud**
   - 访问 [Streamlit Cloud](https://share.streamlit.io/)
   - 使用GitHub账号登录

3. **创建新应用**
   - 点击"New app"
   - 选择您的GitHub仓库
   - 设置主文件路径为 `app.py`
   - 选择Python版本（推荐3.10或以上）

4. **配置环境变量**
   - 在应用设置中找到"Secrets"选项
   - 添加以下环境变量：
     ```
     DASHSCOPE_API_KEY=your_api_key_here
     ```
   - 或者创建`.streamlit/secrets.toml`文件（仅用于本地开发）

5. **部署**
   - 点击"Deploy"按钮
   - 等待部署完成

### Streamlit Cloud配置说明

- Streamlit Cloud会自动读取`requirements.txt`安装依赖
- 环境变量通过Streamlit Cloud的Secrets功能配置
- 应用会自动更新（当代码推送到GitHub时）

## 注意事项

- 首次运行需要下载模型，可能需要一些时间
- 确保有足够的磁盘空间存储向量数据库
- API密钥请妥善保管，不要提交到代码仓库

## 许可证

MIT License
