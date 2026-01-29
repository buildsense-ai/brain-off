"""
创建记忆系统的数据库表

运行方式：
python scripts/create_memory_tables.py
"""
import asyncio
from sqlalchemy import text
from src.database.connection import engine


async def create_memory_tables():
    """创建记忆系统所需的表"""

    async with engine.begin() as conn:
        # 1. 创建 mem_source 表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS mem_source (
                source_id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                turn INT NOT NULL,
                speaker VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                tool_calls JSONB,
                tool_results JSONB,
                embedding vector(1024),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))

        print("✓ 创建 mem_source 表")

        # 2. 创建索引
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_mem_source_session
            ON mem_source(session_id)
        """))


        # 注意：ivfflat 索引在数据量少时不工作，暂时不创建
        # 等数据量达到几千条后再创建索引
        # await conn.execute(text("""
        #     CREATE INDEX IF NOT EXISTS idx_mem_source_embedding
        #     ON mem_source USING ivfflat (embedding vector_cosine_ops)
        # """))

        print("✓ 创建 mem_source 索引")

        # 3. 创建 facts 表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS facts (
                fact_id SERIAL PRIMARY KEY,
                fact_text TEXT NOT NULL,
                source_ids INT[],
                fact_type VARCHAR(50),
                domain VARCHAR(50),
                confidence FLOAT DEFAULT 1.0,
                embedding vector(1024),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))

        print("✓ 创建 facts 表")

        # 4. 创建索引
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_facts_domain
            ON facts(domain)
        """))

        # 注意：ivfflat 索引在数据量少时不工作，暂时不创建
        # await conn.execute(text("""
        #     CREATE INDEX IF NOT EXISTS idx_facts_embedding
        #     ON facts USING ivfflat (embedding vector_cosine_ops)
        # """))

        print("✓ 创建 facts 索引")

    print("\n✅ 记忆系统表创建完成！")


if __name__ == "__main__":
    asyncio.run(create_memory_tables())
