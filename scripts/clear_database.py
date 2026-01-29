"""
清空数据库所有数据

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/clear_database.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.connection import engine


async def clear_all_data():
    """清空所有表数据"""
    print("=== 开始清空数据库 ===\n")

    async with AsyncSession(engine) as session:
        try:
            # 按照依赖顺序删除
            tables = [
                "task_tags",
                "conversations",
                "tasks",
                "tags",
                "facts",
                "mem_source"
            ]

            for table in tables:
                result = await session.execute(text(f"DELETE FROM {table}"))
                count = result.rowcount
                print(f"✓ 清空 {table}: {count} 条记录")

            await session.commit()
            print("\n✅ 数据库清空完成！")

        except Exception as e:
            print(f"\n❌ 清空失败: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(clear_all_data())
