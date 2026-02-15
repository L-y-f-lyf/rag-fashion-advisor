import streamlit as st
import config_data as config
from rag import RagService
import time

# ====================== 页面配置 ======================
st.set_page_config(
    page_title="穿搭智能顾问",
    page_icon="👔",
    layout="wide"
)

# ====================== 超级好看的自定义样式 ======================
st.markdown("""
<style>
/* 全局背景 */
.stApp {
    background-color: #f9fafc;
}

/* 标题 */
.main-title {
    font-size: 34px;
    font-weight: 700;
    text-align: center;
    color: #222;
    margin-bottom: 8px;
}

.sub-title {
    text-align: center;
    color: #666;
    font-size: 15px;
    margin-bottom: 25px;
}

/* 消息气泡 */
.user-box {
    background: #e7f5ff;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 10px 0;
    max-width: 80%;
    float: right;
    clear: both;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.ai-box {
    background: #ffffff;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 0;
    max-width: 80%;
    float: left;
    clear: both;
    border: 1px solid #eee;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* 底部输入框 */
.stChatInputContainer {
    padding-bottom: 15px;
}

/* 复制按钮 */
.copy-btn {
    font-size: 12px;
    color: #888;
    cursor: pointer;
    float: right;
}
</style>
""", unsafe_allow_html=True)

# ====================== 会话初始化 ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_service" not in st.session_state:
    st.session_state.rag_service = RagService()


# ====================== 流式输出函数 ======================
def stream_response(response_text):
    """流式输出回答（打字机效果）"""
    placeholder = st.empty()
    current_text = ""
    for char in response_text:
        current_text += char
        placeholder.markdown(f'<div class="ai-box">{current_text}</div>', unsafe_allow_html=True)
        time.sleep(0.02)  # 控制打字速度，越小越快
    return current_text


# ====================== 顶部栏 ======================
col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

# ====================== 标题 ======================
st.markdown('<div class="main-title">👔 四季穿搭智能顾问</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">基于 RAG 检索 | 穿搭颜色 | 日常搭配 | 男生穿搭指南</div>', unsafe_allow_html=True)

# ====================== 渲染聊天历史 ======================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-box">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-box">{msg["content"]}</div>', unsafe_allow_html=True)

# ====================== 聊天输入 ======================
prompt = st.chat_input("请问我：春天穿什么颜色？日常怎么穿搭？...")

session_config = {
    "configurable": {"session_id": "user_001"}
}

if prompt:
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-box">{prompt}</div>', unsafe_allow_html=True)

    # AI 回答（流式输出）
    with st.spinner("正在思考穿搭方案..."):
        # 调用RAG获取完整回答
        res = st.session_state.rag_service.chain.invoke(
            {"input": prompt},
            config=session_config
        )
        full_answer = res.content

        # 流式显示回答
        final_answer = stream_response(full_answer)

    # 保存完整回答到历史
    st.session_state.messages.append({"role": "assistant", "content": final_answer})

    # 自动刷新让界面更流畅
    st.rerun()