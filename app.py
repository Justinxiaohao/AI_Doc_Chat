import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models.tongyi import ChatTongyi
try:
    from langchain.chains import RetrievalQA
except ModuleNotFoundError:
    from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import tempfile
import shutil
from pathlib import Path

# 加载环境变量
load_dotenv()

# 配置页面
st.set_page_config(
    page_title="RAG文档问答系统",
    page_icon="📚",
    layout="wide"
)

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False
if "document_metadata" not in st.session_state:
    st.session_state.document_metadata = {}

# 配置阿里云百炼API
# 优先使用Streamlit Cloud的secrets，其次使用环境变量
DASHSCOPE_API_KEY = None

# 尝试从Streamlit Secrets获取（Streamlit Cloud）
try:
    if hasattr(st, 'secrets') and 'DASHSCOPE_API_KEY' in st.secrets:
        DASHSCOPE_API_KEY = st.secrets['DASHSCOPE_API_KEY']
except:
    pass

# 如果Secrets中没有，尝试从环境变量获取（本地开发）
if not DASHSCOPE_API_KEY:
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not DASHSCOPE_API_KEY:
    st.error("⚠️ 请设置DASHSCOPE_API_KEY")
    st.info("""
    **本地开发**: 在`.env`文件中设置 `DASHSCOPE_API_KEY=your_api_key`
    
    **Streamlit Cloud**: 在应用设置的Secrets中添加：
    ```toml
    DASHSCOPE_API_KEY = "your_api_key_here"
    ```
    """)
    st.stop()

# 注意：ChatTongyi/DashScope SDK 使用官方默认地址即可。
# 强制设置为 OpenAI 兼容地址会导致 URL 拼接错误（url error）。
# 如需自定义，仅在你确认是 DashScope SDK 可用地址时再设置。
# os.environ["DASHSCOPE_API_BASE"] = "https://dashscope.aliyuncs.com/api/v1"

# 低成本模型可通过环境变量覆盖（例如某个低价 plus 快照版本）
LLM_MODEL_NAME = os.getenv("DASHSCOPE_LLM_MODEL", "qwen-plus")
EMBEDDING_MODEL_NAME = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v3")

# 临时目录用于存储上传的文件和向量数据库
TEMP_DIR = Path(tempfile.gettempdir()) / "rag_system"
TEMP_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH = TEMP_DIR / "chroma_db"

def load_document(file):
    """加载文档并提取文本"""
    file_extension = file.name.split('.')[-1].lower()
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        if file_extension == "pdf":
            loader = PyPDFLoader(tmp_path)
        elif file_extension == "txt":
            loader = TextLoader(tmp_path, encoding='utf-8')
        else:
            st.error(f"不支持的文件格式: {file_extension}")
            return None
        
        documents = loader.load()
        
        # 添加文件名到metadata
        for doc in documents:
            doc.metadata['source_file'] = file.name
            doc.metadata['file_type'] = file_extension
        
        return documents
    except Exception as e:
        st.error(f"加载文档时出错: {str(e)}")
        return None
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def split_documents(documents):
    """将文档按1000字符切片，重叠200字符"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    return splits

def create_vectorstore(documents):
    """创建向量存储"""
    # 初始化embedding模型
    embeddings = DashScopeEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        dashscope_api_key=DASHSCOPE_API_KEY
    )
    
    # 如果已存在向量数据库，先删除
    if VECTOR_DB_PATH.exists():
        shutil.rmtree(VECTOR_DB_PATH)
    
    # 创建新的向量数据库
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_PATH)
    )
    
    return vectorstore

def get_qa_chain(vectorstore):
    """创建问答链"""
    # 初始化大模型
    llm = ChatTongyi(
        model_name=LLM_MODEL_NAME,
        dashscope_api_key=DASHSCOPE_API_KEY,
        temperature=0.7
    )
    
    # 自定义提示模板
    prompt_template = """使用以下上下文信息回答用户的问题。如果你不知道答案，就说你不知道，不要编造答案。

上下文信息：
{context}

问题：{question}

请用中文回答，并说明答案来源于哪个文档的哪部分内容。"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # 创建检索问答链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 3}  # 检索前3个最相关的文档片段
        ),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
        verbose=False
    )
    
    return qa_chain

# 侧边栏 - 文件上传
with st.sidebar:
    st.header("📁 文档上传")
    
    uploaded_files = st.file_uploader(
        "上传PDF或TXT文件",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("处理文档", type="primary"):
        if uploaded_files:
            with st.spinner("正在处理文档..."):
                all_documents = []
                all_metadata = {}
                
                for uploaded_file in uploaded_files:
                    st.write(f"处理中: {uploaded_file.name}")
                    documents = load_document(uploaded_file)
                    
                    if documents:
                        # 切片
                        splits = split_documents(documents)
                        all_documents.extend(splits)
                        
                        # 保存文档元数据
                        all_metadata[uploaded_file.name] = {
                            "chunks": len(splits),
                            "total_chars": sum(len(doc.page_content) for doc in splits)
                        }
                
                if all_documents:
                    # 创建向量存储
                    vectorstore = create_vectorstore(all_documents)
                    st.session_state.vectorstore = vectorstore
                    st.session_state.documents_loaded = True
                    st.session_state.document_metadata = all_metadata
                    st.success(f"成功处理 {len(uploaded_files)} 个文件，共 {len(all_documents)} 个文档片段！")
                else:
                    st.error("未能提取任何文档内容")
        else:
            st.warning("请先上传文件")
    
    st.divider()
    
    # 显示已加载的文档信息
    if st.session_state.documents_loaded:
        st.subheader("已加载文档")
        for filename, metadata in st.session_state.document_metadata.items():
            st.write(f"📄 {filename}")
            st.caption(f"片段数: {metadata['chunks']}, 总字符数: {metadata['total_chars']}")
    
    st.divider()
    
    # 清空对话历史
    if st.button("🗑️ 清空对话历史"):
        st.session_state.messages = []
        st.rerun()
    
    # 清空向量数据库
    if st.button("🗑️ 清空向量数据库", type="secondary"):
        if VECTOR_DB_PATH.exists():
            shutil.rmtree(VECTOR_DB_PATH)
        st.session_state.vectorstore = None
        st.session_state.documents_loaded = False
        st.session_state.document_metadata = {}
        st.session_state.messages = []
        st.success("向量数据库已清空")
        st.rerun()

# 主界面 - 聊天
st.title("📚 RAG文档问答系统")
st.caption("基于LangChain + 阿里云百炼 + ChromaDB构建")

# 检查是否已加载文档
if not st.session_state.documents_loaded:
    st.info("👈 请在左侧边栏上传并处理文档，然后开始提问")
else:
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 显示来源文档
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📎 回答来源"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**来源 {i}:**")
                        st.caption(f"文件: {source.metadata.get('source_file', '未知')}")
                        st.caption(f"页码: {source.metadata.get('page', 'N/A')}")
                        st.text(source.page_content[:300] + "..." if len(source.page_content) > 300 else source.page_content)
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成回答
        with st.chat_message("assistant"):
            with st.spinner("正在思考..."):
                try:
                    # 创建问答链
                    qa_chain = get_qa_chain(st.session_state.vectorstore)
                    
                    # 执行查询
                    result = qa_chain({"query": prompt})
                    
                    answer = result["result"]
                    source_documents = result.get("source_documents", [])
                    
                    # 显示回答
                    st.markdown(answer)
                    
                    # 显示来源
                    if source_documents:
                        with st.expander("📎 回答来源"):
                            for i, source in enumerate(source_documents, 1):
                                st.write(f"**来源 {i}:**")
                                st.caption(f"文件: {source.metadata.get('source_file', '未知')}")
                                st.caption(f"页码: {source.metadata.get('page', 'N/A')}")
                                st.text(source.page_content[:300] + "..." if len(source.page_content) > 300 else source.page_content)
                    
                    # 保存到历史
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": source_documents
                    })
                    
                except Exception as e:
                    error_msg = f"生成回答时出错: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
