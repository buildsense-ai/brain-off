"""
统一 LLM 客户端 - 支持多模型切换

支持的模型：
- DeepSeek (deepseek-reasoner, deepseek-chat)
- Kimi (moonshot-v1-128k, kimi-k2.5)
"""
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import httpx

load_dotenv()


class UnifiedLLMClient:
    """统一的 LLM 客户端，支持多模型"""

    def __init__(
        self,
        provider: str = "deepseek",
        model_name: Optional[str] = None,
        use_reasoner: bool = False
    ):
        """
        初始化 LLM 客户端

        Args:
            provider: 模型提供商 (deepseek, moonshot)
            model_name: 具体模型名称（可选）
            use_reasoner: 是否使用 reasoner 模式（仅 DeepSeek）
        """
        self.provider = provider
        self.use_reasoner = use_reasoner

        # 根据 provider 初始化客户端
        if provider == "deepseek":
            self.client = AsyncOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            )
            self.model = model_name or ("deepseek-reasoner" if use_reasoner else "deepseek-chat")
            self.supports_vision = False
        
        elif provider == "moonshot":
            # 创建不使用代理的 httpx 客户端
            import httpx
            http_client = httpx.AsyncClient(
                timeout=300.0,
                trust_env=False  # 不读取环境变量中的代理配置
            )
            self.client = AsyncOpenAI(
                api_key=os.getenv("VISION_MODEL_API_KEY"),
                base_url=os.getenv("VISION_MODEL_BASE_URL", "https://api.moonshot.cn/v1"),
                http_client=http_client
            )
            self.model = model_name or os.getenv("VISION_MODEL_NAME", "kimi-k2.5")
            self.supports_vision = True
        
        else:
            raise ValueError(f"不支持的 provider: {provider}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        stream: bool = False
    ):
        """
        发送聊天完成请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            tools: 工具定义
            tool_choice: 工具选择策略
            stream: 是否流式输出

        Returns:
            API 响应
        """
        # Kimi k2.5 模型只支持 temperature=1
        if self.model == "kimi-k2.5":
            temperature = 1.0

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

        return await self.client.chat.completions.create(**kwargs)


def create_llm_client(
    skill_config: Optional[Dict[str, Any]] = None,
    use_reasoner: bool = False
) -> UnifiedLLMClient:
    """
    根据 skill 配置创建 LLM 客户端

    Args:
        skill_config: skill 配置（包含 model 和 metadata）
        use_reasoner: 是否使用 reasoner 模式

    Returns:
        UnifiedLLMClient 实例
    """
    # 如果没有 skill 配置，使用默认 DeepSeek
    if not skill_config:
        return UnifiedLLMClient(provider="deepseek", use_reasoner=use_reasoner)

    # 检查是否需要 vision
    metadata = skill_config.get("metadata", {})
    requires_vision = metadata.get("requires_vision", False)

    if requires_vision:
        # 使用多模态模型（Kimi）- 优先使用环境变量配置
        return UnifiedLLMClient(
            provider="moonshot",
            model_name=None  # 使用 UnifiedLLMClient 中的默认逻辑（从环境变量读取）
        )
    else:
        # 使用 DeepSeek
        return UnifiedLLMClient(provider="deepseek", use_reasoner=use_reasoner)
