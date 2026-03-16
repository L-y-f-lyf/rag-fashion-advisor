# Fashion Advisor Agent - Simplified Version
# 使用直接的 LLM + 工具调用方式，避免 AgentExecutor 依赖问题

from typing import Optional, Dict, Any
import config
import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import PromptTemplate

# 导入工具
from tools import get_tools, KnowledgeBaseRetrievalTool, ScenarioStyleMatchingTool, PersonalizedOutfitGeneratorTool


class FashionAdvisorAgent:
    """简化版穿搭顾问 Agent - 不使用 LangChain 的 AgentExecutor"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.DASHSCOPE_API_KEY
        self._initialize_model()
        self._initialize_tools()

    def _initialize_model(self):
        logger.info("Initializing chat model...")
        self.chat_model = ChatTongyi(
            model=config.CHAT_MODEL,
            dashscope_api_key=self.api_key,
            temperature=config.TEMPERATURE
        )
        logger.info(f"Chat model initialized: {config.CHAT_MODEL}")

    def _initialize_tools(self):
        logger.info("Initializing tools...")
        self.knowledge_tool = KnowledgeBaseRetrievalTool(api_key=self.api_key)
        self.matching_tool = ScenarioStyleMatchingTool()
        self.outfit_tool = PersonalizedOutfitGeneratorTool(api_key=self.api_key)
        logger.info("Tools initialized")

    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """分析用户意图，决定使用哪个工具"""
        prompt = f"""你是一个意图分析助手。分析用户的穿搭问题，决定应该使用哪个工具。

用户问题: {user_input}

可用工具:
1. knowledge_base_retrieval - 查询穿搭知识库，适合询问穿搭知识、颜色搭配、面料选择等通用问题
2. scenario_style_matching - 场景风格匹配，适合用户提供了场景、体型、性别、风格信息时
3. personalized_outfitfit_generator - 生成个性化穿搭方案，适合用户需要完整穿搭建议时
4. direct_answer - 直接回答，适合简单问候或不需要工具的问题

请输出 JSON 格式，包含:
- tool: 选择的工具名称 (knowledge_base_retrieval/scenario_style_matching/personalized_outfitfit_generator/direct_answer)
- params: 工具参数 (如果需要场景、体型等信息，请从用户问题中提取)
- reasoning: 选择理由

只输出 JSON，不要其他文字。"""

        try:
            response = self.chat_model.invoke(prompt)
            content = response.content.strip()

            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            logger.warning(f"Intent analysis failed: {e}")

        # 默认使用知识库检索
        return {
            "tool": "knowledge_base_retrieval",
            "params": {"query": user_input},
            "reasoning": "Default to knowledge base"
        }

    def _extract_parameters(self, user_input: str) -> Dict[str, str]:
        """从用户输入中提取场景、体型、性别、风格等参数"""
        prompt = f"""从用户的穿搭问题中提取以下参数（如果有的话）：

用户问题: {user_input}

需要提取的参数:
- gender: 性别 (男/女/male/female)
- scene: 场景 (通勤/约会/运动/正式/休闲/commute/date/sport/formal/casual)
- body_type: 体型 (梨形/苹果形/沙漏形/直筒形/pear/apple/hourglass/straight)
- style: 风格 (极简/轻熟/休闲/韩系/minimal/light mature/casual/Korean)

如果某个参数没有提到，留空字符串。
请输出 JSON 格式。"""

        try:
            response = self.chat_model.invoke(prompt)
            content = response.content.strip()
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                # 翻译英文参数
                translations = {
                    "male": "男", "female": "女",
                    "commute": "通勤", "date": "约会", "sport": "运动", "formal": "正式", "casual": "休闲",
                    "pear": "梨形", "apple": "苹果形", "hourglass": "沙漏形", "straight": "直筒形",
                    "minimal": "极简", "light mature": "轻熟", "korean": "韩系"
                }
                for key, value in result.items():
                    if isinstance(value, str) and value.lower() in translations:
                        result[key] = translations[value.lower()]
                return result
        except Exception as e:
            logger.warning(f"Parameter extraction failed: {e}")

        return {"gender": "", "scene": "", "body_type": "", "style": ""}

    def chat(self, user_input: str, context: dict = None) -> dict:
        result = {
            "success": False,
            "answer": "",
            "error": None,
            "intermediate_steps": []
        }

        try:
            logger.info(f"User input: {user_input}")

            # 分析意图
            intent = self._analyze_user_intent(user_input)
            tool_name = intent.get("tool", "knowledge_base_retrieval")
            params = intent.get("params", {})

            logger.info(f"Selected tool: {tool_name}")

            tool_result = ""
            used_tool = None

            # 执行工具
            if tool_name == "knowledge_base_retrieval":
                query = params.get("query", user_input)
                tool_result = self.knowledge_tool._run(query)
                used_tool = "knowledge_base_retrieval"
            elif tool_name == "scenario_style_matching":
                extracted = self._extract_parameters(user_input)
                scene = params.get("scene", extracted.get("scene", "")) or "通勤"
                body_type = params.get("body_type", extracted.get("body_type", "")) or "直筒形"
                gender = params.get("gender", extracted.get("gender", "")) or "女"
                style = params.get("style", extracted.get("style", "")) or "极简"
                tool_result = self.matching_tool._run(scene, body_type, gender, style)
                used_tool = "scenario_style_matching"
            elif tool_name == "personalized_outfitfit_generator":
                extracted = self._extract_parameters(user_input)
                scene = params.get("scene", extracted.get("scene", "")) or "通勤"
                body_type = params.get("body_type", extracted.get("body_type", "")) or "直筒形"
                gender = params.get("gender", extracted.get("gender", "")) or "女"
                style = params.get("style", extracted.get("style", "")) or "极简"
                additional = params.get("additional_request", "")
                tool_result = self.outfit_tool._run(scene, body_type, gender, style, additional)
                used_tool = "personalized_outfitfit_generator"
            else:
                # 直接回答
                tool_result = ""
                used_tool = "direct_answer"

            result["intermediate_steps"].append([{"tool": used_tool}, tool_result])

            # 生成最终回答
            final_prompt = f"""你是一位专业的穿搭顾问。请根据以下信息为用户提供帮助。

用户问题: {user_input}

参考信息:
{tool_result if tool_result else '直接回答用户问题'}

请给出专业、友好、实用的回答。"""

            response = self.chat_model.invoke(final_prompt)
            result["answer"] = response.content
            result["success"] = True

            logger.info(f"Agent response completed, length: {len(result['answer'])}")

        except Exception as e:
            error_msg = f"Agent execution error: {str(e)}"
            logger.error(error_msg)
            result["error"] = error_msg

            # Fallback 到 RAG 检索
            logger.info("Attempting fallback to RAG retrieval...")
            try:
                rag_result = self.knowledge_tool._run(user_input)
                result["answer"] = f"系统繁忙，以下是知识库检索结果：\n\n{rag_result}"
                result["success"] = True
                result["error"] = "Fallback to RAG mode"
                logger.info("RAG fallback successful")
            except Exception as rag_error:
                result["answer"] = "抱歉，系统暂时无法回答您的问题，请稍后再试。"
                result["error"] = f"RAG fallback also failed: {str(rag_error)}"
                logger.error(f"RAG fallback failed: {str(rag_error)}")

        return result

    def get_tool_names(self) -> list:
        return ["knowledge_base_retrieval", "scenario_style_matching", "personalized_outfitfit_generator"]

    def get_tool_descriptions(self) -> dict:
        return {
            "knowledge_base_retrieval": "从向量数据库检索穿搭知识",
            "scenario_style_matching": "匹配场景、体型、性别和风格提供穿搭原则",
            "personalized_outfitfit_generator": "根据用户信息生成个性化穿搭方案"
        }


# ================ 单例模式 ================
_agent_instance = None


def get_agent(api_key: Optional[str] = None) -> FashionAdvisorAgent:
    global _agent_instance

    if _agent_instance is None or api_key is not None:
        _agent_instance = FashionAdvisorAgent(api_key=api_key)

    return _agent_instance


def reset_agent():
    global _agent_instance
    _agent_instance = None


if __name__ == "__main__":
    import os

    test_api_key = os.getenv("DASHSCOPE_API_KEY", "your-test-api-key")

    print("=" * 60)
    print("Initializing Fashion Advisor Agent")
    print("=" * 60)
    agent = FashionAdvisorAgent(api_key=test_api_key)

    print("\nAvailable tools:")
    for tool_name, tool_desc in agent.get_tool_descriptions().items():
        print(f"- {tool_name}: {tool_desc}")

    print("\n" + "=" * 60)
    print("Testing chat")
    print("=" * 60)

    print("\nQuestion 1: 春天适合穿什么颜色？")
    result1 = agent.chat("春天适合穿什么颜色？")
    print(f"Success: {result1['success']}")
    print(f"Answer: {result1['answer'][:200]}...")
    if result1.get('error'):
        print(f"Error: {result1['error']}")