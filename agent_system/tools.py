# Fashion Advisor Agent Tools - Simplified
# 移除对 langchain_core.pydantic_v1 的依赖

from typing import Optional, Type
import config
import logging

logger = logging.getLogger(__name__)

# 直接使用标准 pydantic
try:
    from pydantic import BaseModel, Field
    logger.info("Using pydantic v2")
except ImportError:
    from pydantic.v1 import BaseModel, Field
    logger.info("Using pydantic v1")


# 简化的 BaseTool 替代类，不依赖 langchain
class SimpleTool:
    """简化的工具基类"""
    name: str = ""
    description: str = ""

    def _run(self, *args, **kwargs):
        raise NotImplementedError

    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._run(*args, **kwargs)


# Tool 1: Knowledge Base Retrieval
class KnowledgeBaseRetrievalInput(BaseModel):
    query: str = Field(description="User's fashion question")


class KnowledgeBaseRetrievalTool(SimpleTool):
    name = "knowledge_base_retrieval"
    description = "Retrieve fashion knowledge from vector database. Returns top 3 relevant knowledge."

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or config.DASHSCOPE_API_KEY
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """初始化向量存储"""
        try:
            from langchain_community.embeddings import DashScopeEmbeddings
            # 尝试导入 Chroma，如果失败就用模拟方式
            try:
                import chromadb
                from langchain_chroma import Chroma
                self.embedding = DashScopeEmbeddings(
                    model=config.EMBEDDING_MODEL,
                    dashscope_api_key=self.api_key
                )
                self.vector_store = Chroma(
                    collection_name=config.COLLECTION_NAME,
                    embedding_function=self.embedding,
                    persist_directory=config.PERSIST_DIRECTORY
                )
                self.use_chroma = True
                logger.info("Chroma vector store initialized")
            except Exception as e:
                logger.warning(f"Chroma not available, using fallback: {e}")
                self.use_chroma = False
                self.vector_store = None
        except Exception as e:
            logger.warning(f"Embeddings not available: {e}")
            self.use_chroma = False
            self.vector_store = None

    def _run(self, query: str) -> str:
        if not self.use_chroma or self.vector_store is None:
            return self._fallback_knowledge(query)

        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=config.SIMILARITY_THRESHOLD
            )

            if not results:
                return self._fallback_knowledge(query)

            knowledge_list = []
            for i, doc in enumerate(results, 1):
                content = doc.page_content
                metadata = doc.metadata.get('source', 'Unknown')
                knowledge_list.append(f"[Knowledge {i}]\nSource: {metadata}\nContent: {content}")

            return "\n\n".join(knowledge_list)

        except Exception as e:
            logger.error(f"Error retrieving from knowledge base: {e}")
            return self._fallback_knowledge(query)

    def _fallback_knowledge(self, query: str) -> str:
        """备用知识库"""
        knowledge = {
            "颜色": """春季推荐颜色：柔和的粉色、浅蓝色、淡黄色、薄荷绿等清新色系；\n夏季推荐颜色：白色、浅蓝、浅粉、薄荷绿等清爽色系；\n秋季推荐颜色：焦糖色、棕色、酒红色、墨绿色等暖色系；\n冬季推荐颜色：黑色、灰色、深蓝色、酒红色等深沉色系。""",
            "搭配": """穿搭搭配原则：\n1. 颜色不超过3种主色；\n2. 上下身松紧搭配；\n3. 注重腰线位置；\n4. 配饰点缀整体造型。""",
            "体型": """梨形身材：上浅下深，A字裙、直筒裤；\n苹果形身材：V领上衣，高腰下装；\n沙漏形身材：修身剪裁，突出腰线；\n直筒形身材：创造曲线感，层叠搭配。""",
            "场景": """通勤：简约大方，中性色为主；\n约会：精致有女人味，柔和色系；\n运动：舒适透气，亮色增加活力；\n正式：庄重正式，深色为主；\n休闲：舒适自在，颜色活泼。"""
        }

        result = []
        for key, value in knowledge.items():
            if key in query:
                result.append(value)

        if not result:
            result.append("穿搭建议：根据场合选择合适的服装，注重颜色搭配和谐，突出个人优点。")

        return "\n\n".join(result)

    async def _arun(self, query: str) -> str:
        return self._run(query)


# Tool 2: Scenario Style Matching
class ScenarioStyleMatchingInput(BaseModel):
    scene: str = Field(description="Scene: commute/date/sport/formal/casual")
    body_type: str = Field(description="Body type: pear/apple/hourglass/straight")
    gender: str = Field(description="Gender: male/female")
    style: str = Field(description="Style: minimal/light mature/casual/Korean")


class ScenarioStyleMatchingTool(SimpleTool):
    name = "scenario_style_matching"
    description = "Match scene, body type, gender, and style to provide fashion principles."

    def _run(self, scene: str, body_type: str, gender: str, style: str) -> str:
        result_parts = []

        # Scene rules
        if scene in config.SCENE_RULES:
            scene_info = config.SCENE_RULES[scene]
            result_parts.append(f"[Scene Matching - {scene}]")
            result_parts.append(f"Description: {scene_info['description']}")
            result_parts.append("Fashion Principles:")
            for i, principle in enumerate(scene_info['principles'], 1):
                result_parts.append(f"  {i}. {principle}")
            result_parts.append("")
        else:
            result_parts.append(f"[Scene Matching] No rule found for '{scene}'\n")

        # Body type rules
        if body_type in config.BODY_TYPE_RULES:
            body_info = config.BODY_TYPE_RULES[body_type]
            result_parts.append(f"[Body Type Matching - {body_type}]")
            result_parts.append(f"Description: {body_info['description']}")
            result_parts.append("Fashion Principles:")
            for i, principle in enumerate(body_info['principles'], 1):
                result_parts.append(f"  {i}. {principle}")
            result_parts.append("")
        else:
            result_parts.append(f"[Body Type Matching] No rule found for '{body_type}'\n")

        # Gender rules
        if gender in config.GENDER_RULES:
            gender_info = config.GENDER_RULES[gender]
            result_parts.append(f"[Gender Matching - {gender}]")
            result_parts.append(f"Description: {gender_info['description']}")
            result_parts.append("Fashion Principles:")
            for i, principle in enumerate(gender_info['principles'], 1):
                result_parts.append(f"  {i}. {principle}")
            result_parts.append("")
        else:
            result_parts.append(f"[Gender Matching] No rule found for '{gender}'\n")

        # Style rules
        if style in config.STYLE_RULES:
            style_info = config.STYLE_RULES[style]
            result_parts.append(f"[Style Matching - {style}]")
            result_parts.append(f"Description: {style_info['description']}")
            result_parts.append("Fashion Principles:")
            for i, principle in enumerate(style_info['principles'], 1):
                result_parts.append(f"  {i}. {principle}")
            result_parts.append("")
        else:
            result_parts.append(f"[Style Matching] No rule found for '{style}'\n")

        return "\n".join(result_parts)

    async def _arun(self, scene: str, body_type: str, gender: str, style: str) -> str:
        return self._run(scene, body_type, gender, style)


# Tool 3: Personalized Outfit Generator
class PersonalizedOutfitGeneratorInput(BaseModel):
    scene: str = Field(description="Scene: commute/date/sport/formal/casual")
    body_type: str = Field(description="Body type: pear/apple/hourglass/straight")
    gender: str = Field(description="Gender: male/female")
    style: str = Field(description="Style: minimal/light mature/casual/Korean")
    additional_request: str = Field(default="", description="Additional requirements or notes")


class PersonalizedOutfitGeneratorTool(SimpleTool):
    name = "personalized_outfitfit_generator"
    description = "Generate personalized outfit plan based on user's scene, body type, gender, and style."

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or config.DASHSCOPE_API_KEY

    def _get_chat_model(self):
        """获取聊天模型"""
        try:
            from langchain_community.chat_models import ChatTongyi
            return ChatTongyi(
                model=config.CHAT_MODEL,
                dashscope_api_key=self.api_key,
                temperature=config.TEMPERATURE
            )
        except Exception:
            return None

    def _run(self, scene: str, body_type: str, gender: str, style: str, additional_request: str = "") -> str:
        chat_model = self._get_chat_model()

        if chat_model is None:
            return self._fallback_outfit(scene, body_type, gender, style, additional_request)

        try:
            prompt = f"""你是一位专业的穿搭顾问。请根据以下信息生成个性化穿搭方案。

用户信息:
- 性别: {gender}
- 场景: {scene}
- 体型: {body_type}
- 风格: {style}
- 额外需求: {additional_request if additional_request else '无'}

请生成结构化的穿搭方案，包含:
1. [穿搭原则] 根据场景、体型、性别、风格总结核心穿搭原则（3-5条）
2. [单品推荐] 具体的单品推荐（上装、下装、鞋子、配饰），并说明理由
3. [色彩建议] 推荐的色彩搭配（主色、辅色、点缀色）
4. [穿搭技巧] 具体的穿搭技巧和注意事项（3-5条）

要求:
- 方案要实用、可操作
- 语言专业简洁
"""

            response = chat_model.invoke(prompt)
            return response.content

        except Exception as e:
            logger.error(f"Error generating outfit plan: {e}")
            return self._fallback_outfit(scene, body_type, gender, style, additional_request)

    def _fallback_outfit(self, scene: str, body_type: str, gender: str, style: str, additional_request: str) -> str:
        """备用穿搭方案生成"""
        return f"""[穿搭原则]
1. 根据{scene}场景选择合适的服装
2. 考虑{body_type}体型特点
3. 体现{style}风格
4. 适合{gender}性穿搭

[单品推荐]
上装：根据季节选择适合{style}风格的上衣
下装：选择能修饰{body_type}体型的裤装
鞋子：{scene}场景适用的鞋子
配饰：简约配饰点缀

[色彩建议]
主色：中性色
辅色：根据季节选择
点缀色：小面积亮色

[穿搭技巧]
1. 注重整体搭配协调性
2. 突出个人优点
3. 细节决定成败
4. 舒适与美观并重"""

    async def _arun(self, scene: str, body_type: str, gender: str, style: str, additional_request: str = "") -> str:
        return self._run(scene, body_type, gender, style, additional_request)


# Tool Factory
def get_tools(api_key: Optional[str] = None):
    return [
        KnowledgeBaseRetrievalTool(api_key=api_key),
        ScenarioStyleMatchingTool(),
        PersonalizedOutfitGeneratorTool(api_key=api_key)
    ]


# Test code
if __name__ == "__main__":
    import os

    test_api_key = os.getenv("DASHSCOPE_API_KEY", "your-test-api-key")

    print("=" * 60)
    print("Testing Tools")
    print("=" * 60)

    print("\nTest 1: Knowledge Base Retrieval Tool")
    tool1 = KnowledgeBaseRetrievalTool(api_key=test_api_key)
    result1 = tool1._run("春天适合穿什么颜色？")
    print(result1[:300] if len(result1) > 300 else result1)