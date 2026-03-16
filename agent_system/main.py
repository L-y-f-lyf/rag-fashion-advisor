# ==================== 穿搭智能顾问 Agent 系统 - FastAPI 主应用 ====================

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import os
import sys
import logging
import traceback

# 添加当前目录到 Python 路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 导入配置和 Agent
import config
from agent import get_agent, reset_agent

# ==================== 配置日志 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ==================== 创建 FastAPI 应用 ====================
app = FastAPI(
    title="穿搭智能顾问 Agent 系统",
    description="基于 LangChain Agent 的智能穿搭推荐系统，支持 RAG 知识库检索和个性化穿搭方案生成",
    version="1.0.0"
)

# ==================== 配置 CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局变量 ============================= ====================
agent_instance = None


# ==================== 请求和响应模型 ====================
class AgentChatRequest(BaseModel):
    """Agent 聊天请求模型"""
    message: str = Field(..., description="用户消息")
    api_key: Optional[str] = Field(None, description="通义千问 API 密钥（可选）")


class AgentChatResponse(BaseModel):
    """Agent 聊天响应模型"""
    success: bool = Field(..., description="是否成功")
    answer: str = Field(..., description="回答内容")
    error: Optional[str] = Field(None, description="错误信息（如果有）")
    tool_used: Optional[str] = Field(None, description="使用的工具")
    intermediate_steps: Optional[list] = Field(None, description="中间步骤（调试用）")


class RAGChatRequest(BaseModel):
    """RAG 聊天请求模型"""
    query: str = Field(..., description="查询内容")
    api_key: Optional[str] = Field(None, description="通义千问 API 密钥（可选）")


class RAGChatResponse(BaseModel):
    """RAG 聊天响应模型"""
    success: bool = Field(..., description="是否成功")
    answer: str = Field(..., description="回答内容")
    error: Optional[str] = Field(None, description="错误信息（如果有）")


class OutfitGenerationRequest(BaseModel):
    """穿搭方案生成请求模型"""
    gender: str = Field(..., description="性别：男/女")
    scene: str = Field(..., description="场景：通勤/约会/运动/正式/休闲")
    body_type: str = Field(..., description="体型：梨形/苹果形/沙漏形/直筒形")
    style: str = Field(..., description="风格：极简/轻熟/休闲/韩系")
    additional_request: Optional[str] = Field("", description="额外需求")
    api_key: Optional[str] = Field(None, description="通义千问 API 密钥（可选）")


class OutfitGenerationResponse(BaseModel):
    """穿搭方案生成响应模型"""
    success: bool = Field(..., description="是否成功")
    answer: str = Field(..., description="穿搭方案内容")
    error: Optional[str] = Field(None, description="错误信息（如果有）")


# ==================== 全局异常处理 ====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    error_detail = f"{type(exc).__name__}: {str(exc)}"
    logger.error(f"500 错误：{error_detail}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": str(exc),
            "error_type": type(exc).__name__,
            "answer": "服务器内部错误，请稍后再试"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    logger.warning(f"{exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "answer": exc.detail
        }
    )


# ==================== 启动事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    try:
        logger.info("=" * 60)
        logger.info("正在初始化穿搭智能顾问 Agent 系统...")
        logger.info("=" * 60)

        # logger.info(f"Chroma 向量库路径：{config.PERSIST_DIRECTORY}")
        # logger.info(f"Chroma 集合名称：{config.COLLECTION_NAME}")
        # logger.info(f"检索 Top K：{config.SIMILARITY_THRESHOLD}")
        # logger.info(f"嵌入模型：{config.EMBEDDING_MODEL}")
        # logger.info(f"聊天模型：{config.CHAT_MODEL}")
        # logger.info(f"Agent 温度：{config.TEMPERATURE}")

        # 挂载静态文件
        static_dir = os.path.join(BASE_DIR, "static")
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            logger.info(f"静态文件目录：{static_dir}")

        logger.info("=" * 60)
        logger.info("应用启动完成！")
        logger.info(f"访问地址：http://{config.HOST}:{config.PORT}")
        logger.info(f"API 文档：http://{config.HOST}:{config.PORT}/docs")
        logger.info(f"前端页面：http://{config.HOST}:{config.PORT}/")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"启动失败：{e}")
        logger.error(traceback.format_exc())
        raise


# ==================== 根路由 ====================
@app.get("/")
async def root():
    """根路由，返回前端页面"""
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "穿搭智能顾问 Agent 系统",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "agent_chat": "/agent/chat",
            "rag_chat": "/rag/chat",
            "outfit_generation": "/outfit/generate"
        }
    }


@app.get("/health")
async def health():
    """健康检查接口"""
    return {
        "status": "ok",
        "system": "穿搭智能顾问 Agent 系统",
        "version": "1.0.0"
    }


# ==================== Agent 聊天接口 ====================
@app.post("/agent/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """
    Agent 智能聊天接口

    Agent 会根据用户输入自主判断使用哪个工具，并给出智能回答

    - 穿搭知识查询：使用 RAG 检索工具
    - 个性化穿搭建议：使用穿搭方案生成工具
    - 场景体型风格查询：使用匹配工具
    """
    global agent_instance

    try:
        logger.info(f"收到 Agent 聊天请求：{request.message[:50]}...")

        # 如果用户提供了 API Key 或 Agent 未初始化，则重新初始化
        api_key = request.api_key or config.DASHSCOPE_API_KEY
        if api_key and (agent_instance is None or request.api_key):
            agent_instance = get_agent(api_key=api_key)
            logger.info("Agent 初始化完成")

        if agent_instance is None:
            agent_instance = get_agent()

        # 调用 Agent
        result = agent_instance.chat(request.message)

        # 构建响应
        response = AgentChatResponse(
            success=result["success"],
            answer=result["answer"],
            error=result.get("error")
        )

        # 如果有中间步骤，记录使用的工具
        if result.get("intermediate_steps"):
            tool_used = []
            for step in result["intermediate_steps"]:
                if step[0]:
                    tool_used.append(step[0].tool)
            response.tool_used = ", ".join(tool_used) if tool_used else None
            response.intermediate_steps = result["intermediate_steps"]

        logger.info(f"Agent 回答完成，工具使用：{response.tool_used or '无'}")

        return response

    except Exception as e:
        logger.error(f"Agent 聊天出错：{str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RAG 聊天接口 ====================
@app.post("/rag/chat", response_model=RAGChatResponse)
async def rag_chat(request: RAGChatRequest):
    """
    RAG 知识库聊天接口（保留原有功能）

    直接从 Chroma 向量库检索相关穿搭知识
    """
    try:
        logger.info(f"收到 RAG 聊天请求：{request.query[:50]}...")

        # 使用 API Key
        api_key = request.api_key or config.DASHSCOPE_API_KEY

        # 导入 RAG 工具
        from tools import KnowledgeBaseRetrievalTool
        from langchain_community.chat_models import ChatTongyi

        # 初始化检索工具
        retrieval_tool = KnowledgeBaseRetrievalTool(api_key=api_key)

        # 检索相关知识
        knowledge = retrieval_tool._run(request.query)

        # 如果知识为空，返回提示
        if not knowledge or "未找到" in knowledge:
            return RAGChatResponse(
                success=True,
                answer="抱歉，在知识库中没有找到相关穿搭信息。您可以尝试换个问题或提供更多细节。",
                error=None
            )

        # 初始化大模型生成回答
        chat_model = ChatTongyi(
            model=config.CHAT_MODEL,
            dashscope_api_key=api_key,
            temperature=config.TEMPERATURE
        )

        # 构建提示词

        prompt = f"""
你是一位专业的穿搭顾问。请根据以下参考资料回答用户的问题。

参考资料：
{knowledge}

用户问题：
{request.query}

要求：
1. 基于参考资料回答
2. 回答要专业、简洁、易懂
3. 如果参考资料不够充分，可以补充一些通用建议
4. 不要编造信息
"""

        # 生成回答
        response = chat_model.invoke(prompt)
        answer = response.content

        logger.info("RAG 聊天回答完成")

        return RAGChatResponse(
            success=True,
            answer=answer,
            error=None
        )

    except Exception as e:
        logger.error(f"RAG 聊天出错：{str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 穿搭方案生成接口 ====================
@app.post("/outfit/generate", response_model=OutfitGenerationResponse)
async def outfit_generation(request: OutfitGenerationRequest):
    """
    穿搭方案生成接口

    根据用户提供的场景、体型、性别、风格等信息，生成个性化的穿搭方案

    参数：
    - gender: 性别（男/女）
    - scene: 场景（通勤/约会/运动/正式/休闲）
    - body_type: 体型（梨形/苹果形/沙漏形/直筒形）
    - style: 风格（极简/轻熟/休闲/韩系）
    - additional_request: 额外需求（可选）
    """
    try:
        logger.info(f"收到穿搭方案生成请求：{request.gender} / {request.scene} / {request.body_type} / {request.style}")

        # 使用 API Key
        api_key = request.api_key or config.DASHSCOPE_API_KEY

        # 导入工具
        from tools import PersonalizedOutfitGeneratorTool

        # 初始化工具
        generator_tool = PersonalizedOutfitGeneratorTool(api_key=api_key)

        # 生成穿搭方案
        answer = generator_tool._run(
            scene=request.scene,
            body_type=request.body_type,
            gender=request.gender,
            style=request.style,
            additional_request=request.additional_request or ""
        )

        logger.info("穿搭方案生成完成")

        return OutfitGenerationResponse(
            success=True,
            answer=answer,
            error=None
        )

    except Exception as e:
        logger.error(f"穿搭方案生成出错：{str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    import uvicorn

    logger.info("正在启动服务器...")
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )