"""
记忆服务 - 负责记忆的写入和检索

功能：
1. 写入对话到 mem_source
2. 写入事实到 facts
3. 检索相关记忆（混合 facts + sources）
"""
from typing import List, Dict, Any, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from src.services.embedding_service import EmbeddingService


def _format_vector(embedding: List[float]) -> str:
    """将 embedding 列表转换为 PostgreSQL vector 格式的字符串"""
    return '[' + ','.join(str(x) for x in embedding) + ']'


def _format_jsonb(data: Optional[Any]) -> Optional[str]:
    """将 Python 对象转换为 JSON 字符串用于 JSONB 类型"""
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)


class MemoryService:
    """记忆服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()

    async def write_conversation(
        self,
        session_id: str,
        turn: int,
        speaker: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None
    ) -> int:
        """
        写入对话到 mem_source 表

        Args:
            session_id: 会话ID
            turn: 对话轮次
            speaker: 说话者 ('user' or 'assistant')
            content: 对话内容
            tool_calls: 工具调用（如果有）
            tool_results: 工具结果（如果有）

        Returns:
            source_id: 插入的记录ID
        """
        # 生成 embedding
        embedding = await self.embedding_service.generate(content)
        embedding_str = _format_vector(embedding)

        # 插入数据库
        result = await self.db.execute(
            text("""
                INSERT INTO mem_source
                (session_id, turn, speaker, content, tool_calls, tool_results, embedding)
                VALUES (:session_id, :turn, :speaker, :content, CAST(:tool_calls AS jsonb), CAST(:tool_results AS jsonb), CAST(:embedding AS vector))
                RETURNING source_id
            """),
            {
                "session_id": session_id,
                "turn": turn,
                "speaker": speaker,
                "content": content,
                "tool_calls": _format_jsonb(tool_calls),
                "tool_results": _format_jsonb(tool_results),
                "embedding": embedding_str
            }
        )

        await self.db.commit()
        source_id = result.scalar_one()
        return source_id

    async def write_fact(
        self,
        fact_text: str,
        source_ids: List[int],
        fact_type: Optional[str] = None,
        domain: Optional[str] = None,
        confidence: float = 1.0
    ) -> int:
        """
        写入事实到 facts 表

        Args:
            fact_text: 事实内容
            source_ids: 关联的源对话ID列表
            fact_type: 事实类型（如 'user_preference', 'tool_usage'）
            domain: 领域（如 'todo', 'writing'）
            confidence: 置信度

        Returns:
            fact_id: 插入的记录ID
        """
        # 生成 embedding
        embedding = await self.embedding_service.generate(fact_text)
        embedding_str = _format_vector(embedding)

        # 插入数据库
        result = await self.db.execute(
            text("""
                INSERT INTO facts
                (fact_text, source_ids, fact_type, domain, confidence, embedding)
                VALUES (:fact_text, :source_ids, :fact_type, :domain, :confidence, CAST(:embedding AS vector))
                RETURNING fact_id
            """),
            {
                "fact_text": fact_text,
                "source_ids": source_ids,
                "fact_type": fact_type,
                "domain": domain,
                "confidence": confidence,
                "embedding": embedding_str
            }
        )

        await self.db.commit()
        fact_id = result.scalar_one()
        return fact_id

    async def retrieve_memories(
        self,
        query: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        检索相关记忆（混合 facts + sources）

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            包含 facts 和 sources 的字典
        """
        # 生成 query embedding
        query_embedding = await self.embedding_service.generate(query)
        query_embedding_str = _format_vector(query_embedding)

        # 从 facts 表检索
        facts_result = await self.db.execute(
            text("""
                SELECT
                    fact_id,
                    fact_text,
                    fact_type,
                    domain,
                    source_ids,
                    confidence,
                    1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM facts
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {
                "embedding": query_embedding_str,
                "top_k": top_k
            }
        )

        facts = [
            {
                "fact_id": row[0],
                "fact_text": row[1],
                "fact_type": row[2],
                "domain": row[3],
                "source_ids": row[4],
                "confidence": row[5],
                "similarity": row[6]
            }
            for row in facts_result.fetchall()
        ]

        # 从 mem_source 表检索
        sources_result = await self.db.execute(
            text("""
                SELECT
                    source_id,
                    session_id,
                    turn,
                    speaker,
                    content,
                    tool_calls,
                    tool_results,
                    1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM mem_source
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {
                "embedding": query_embedding_str,
                "top_k": top_k
            }
        )

        sources = [
            {
                "source_id": row[0],
                "session_id": row[1],
                "turn": row[2],
                "speaker": row[3],
                "content": row[4],
                "tool_calls": row[5],
                "tool_results": row[6],
                "similarity": row[7]
            }
            for row in sources_result.fetchall()
        ]

        return {
            "facts": facts,
            "sources": sources
        }
