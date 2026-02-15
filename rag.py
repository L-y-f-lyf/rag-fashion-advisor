# 1. 导入核心模块
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableWithMessageHistory
from langchain_core.documents import Document
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from file_history_store import get_history
import config_data as config
from vector_store import VectorStoreService
# rag.py
from langchain_community.embeddings import DashScopeEmbeddings

class RagService:
    def __init__(self, api_key):  # 新增api_key参数
        self.embedding = DashScopeEmbeddings(
            model=config.embedding_model_name,
            dashscope_api_key=api_key  # 使用传入的api_key
        )
        # 其他初始化逻辑...

# 定义打印提示词的函数
def print_prompt(prompt):
    """打印提示词并返回原prompt，不中断链执行"""
    print("="*50)
    print("📜 最终传给大模型的完整提示词（格式化）：")
    print(prompt.to_string())
    print("="*50)
    print("🔍 提示词原始结构：")
    print(prompt)
    print("="*50)
    return prompt

class RagService(object):
    def __init__(self):
        # 2. 初始化向量检索服务
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(
                model=config.embedding_model_name,
                dashscope_api_key=config.dashscope_api_key
            )
        )

        # 3. 定义提示词模板
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料：{context}."),
            ("system","并且我提供用户的对话历史记录，如下："),
            MessagesPlaceholder(variable_name="history"),
            ("user", "请回答用户提问：{input}")
        ])

        # 4. 初始化大模型
        self.chat_model = ChatTongyi(
            model=config.chat_model_name,
            dashscope_api_key=config.dashscope_api_key,
            temperature=0.1
        )

        # 5. 构建执行链
        self.chain = self._get_chain()

    def _get_chain(self):
        """构建完整管道符链（修复管道符和函数调用错误）"""
        retriever = self.vector_service.get_retriever()

        # 文档格式化函数
        def format_docs(docs: list[Document]):
            if not docs:
                return "无相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段: {doc.page_content}\n文档元数据: {doc.metadata}\n\n"
            return formatted_str

        # 核心修复：
        # 1. 先通过retriever获取文档列表，再手动调用format_docs处理
        # 2. 管道符|只能用于Runnable对象，不能直接用于列表和普通函数
        def get_context(input_str: str):
            """封装检索+格式化逻辑"""
            docs = retriever.invoke(input_str)  # 获取文档列表
            return format_docs(docs)  # 手动调用格式化函数

        chain = (
            RunnablePassthrough.assign(
                # 用RunnableLambda包装get_context，转为可运行对象
                context=lambda x: RunnableLambda(get_context).invoke(x["input"])
            )
            | self.prompt_template          # 填充提示词模板
            | RunnableLambda(print_prompt)  # 打印提示词
            | self.chat_model               # 传给大模型
        )

        # 包装成带消息历史的链
        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="output"
        )
        return conversation_chain

if __name__ == "__main__":
    # 1. 定义会话配置
    session_config = {
        "configurable": {
            "session_id": "user_001",
        }
    }

    # 2. 调用链
    rag_service = RagService()
    res = rag_service.chain.invoke(
        {"input": "春天穿什么颜色的衣服"},
        config=session_config
    )

    # 3. 打印最终回答
    print("\n✅ 最终回答：", res.content)