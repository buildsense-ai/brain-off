"""
Gradio GUI for GauzAssist Chatbot
支持异步操作的 GUI 版本

特性：
- 原生异步支持
- 多标签页界面（聊天 + 仪表盘）
- 与 CLI 共享核心逻辑
"""
import gradio as gr
import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from typing import List, Tuple

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.core.utils.performance_tracker import PerformanceTracker
import time


def format_active_progress() -> tuple[str, str]:
    """格式化当前活跃请求的进度

    Returns:
        (chat_display, dashboard_display): 聊天界面显示和仪表盘显示
    """
    active_requests = PerformanceTracker.get_active_requests()

    if not active_requests:
        return "", "暂无活跃请求"

    # 只显示最新的活跃请求
    req = active_requests[-1]
    elapsed = time.time() - req.start_time

    # Dashboard 详细显示
    dashboard_output = f"### 🔄 请求 #{req.request_id}\n\n"
    dashboard_output += f"**查询**: {req.user_query}\n\n"
    dashboard_output += f"**已耗时**: {elapsed:.1f}s\n\n"

    # 主流程进度
    total_sync = len(req.sync_steps)
    completed_sync = sum(1 for s in req.sync_steps if s.status == "completed")
    progress_pct = (completed_sync / total_sync * 100) if total_sync > 0 else 0

    dashboard_output += f"**主流程**: {completed_sync}/{total_sync} 步骤 ({progress_pct:.0f}%)\n\n"

    # 显示所有步骤
    for step in req.sync_steps:
        if step.status == "completed":
            icon = "✅"
            duration = f"{step.duration:.2f}s"
        elif step.status == "in_progress":
            icon = "⏳"
            step_elapsed = time.time() - step.start_time
            duration = f"{step_elapsed:.1f}s..."
        else:
            icon = "⏸️"
            duration = "等待中"

        dashboard_output += f"- {icon} {step.name}: {duration}\n"

    # 异步步骤
    if req.async_steps:
        dashboard_output += f"\n**后台任务**:\n\n"
        for step in req.async_steps:
            if step.status == "completed":
                icon = "✅"
                duration = f"{step.duration:.2f}s"
            elif step.status == "in_progress":
                icon = "🔄"
                step_elapsed = time.time() - step.start_time
                duration = f"{step_elapsed:.1f}s..."
            else:
                icon = "⏸️"
                duration = "等待中"

            dashboard_output += f"- {icon} {step.name}: {duration}\n"

    # 聊天界面简化显示
    chat_output = f"⏱️ 处理中... {elapsed:.0f}s ({progress_pct:.0f}%)"

    return chat_output, dashboard_output


def format_performance_data() -> str:
    """格式化性能追踪数据为 Markdown"""
    requests = PerformanceTracker.get_recent_requests(limit=10)

    if not requests:
        return "### 📊 性能追踪\n\n暂无数据"

    output = "### 📊 最近请求性能追踪\n\n"

    for req in reversed(requests):  # 最新的在前
        status_icon = "✅" if req.status == "completed" else "❌"
        output += f"#### {status_icon} 请求 #{req.request_id}\n"
        output += f"- **查询**: {req.user_query[:50]}...\n"
        output += f"- **时间**: {req.timestamp}\n"
        output += f"- **总耗时**: {req.total_duration:.2f}s\n\n"

        # 同步步骤
        output += "**主流程**:\n"
        for step in req.sync_steps:
            icon = "✅" if step.status == "completed" else "⏳" if step.status == "in_progress" else "❌"
            duration = f"{step.duration:.2f}s" if step.duration else "..."
            output += f"- {icon} {step.name}: {duration}\n"

        # 异步步骤
        if req.async_steps:
            output += "\n**后台任务**:\n"
            for step in req.async_steps:
                icon = "✅" if step.status == "completed" else "⏳" if step.status == "in_progress" else "❌"
                duration = f"{step.duration:.2f}s" if step.duration else "..."
                output += f"- {icon} {step.name}: {duration}\n"

        output += "\n---\n\n"

    return output


def format_context_content(request_id: str = None) -> str:
    """格式化上下文内容为 Markdown

    Args:
        request_id: 请求 ID，如果为 None 则显示最新请求
    """
    requests = PerformanceTracker.get_recent_requests(limit=10)

    if not requests:
        return "### 📝 上下文内容\n\n暂无数据"

    # 找到指定的请求，或使用最新的
    target_req = None
    if request_id:
        for req in requests:
            if req.request_id == request_id:
                target_req = req
                break
    else:
        target_req = requests[-1]  # 最新的请求

    if not target_req or not target_req.context_content:
        return "### 📝 上下文内容\n\n暂无上下文数据"

    ctx = target_req.context_content
    output = f"### 📝 请求 #{target_req.request_id} 的上下文内容\n\n"
    output += f"**查询**: {target_req.user_query}\n\n"
    output += "---\n\n"

    # 1. 技能 Prompt
    if ctx.get("skill_prompt"):
        output += "#### 🎯 技能 Prompt\n\n"
        output += f"```\n{ctx['skill_prompt'][:500]}...\n```\n\n" if len(ctx['skill_prompt']) > 500 else f"```\n{ctx['skill_prompt']}\n```\n\n"
    else:
        output += "#### 🎯 技能 Prompt\n\n无\n\n"

    # 2. 线上记忆
    output += "#### 🌐 线上记忆\n\n"
    online_memories = ctx.get("online_memories", [])
    if online_memories:
        output += f"共 {len(online_memories)} 条记忆:\n\n"
        for i, mem in enumerate(online_memories[:5], 1):  # 只显示前5条
            content = mem.get("content", mem.get("text", ""))
            output += f"{i}. {content[:100]}...\n" if len(content) > 100 else f"{i}. {content}\n"
        if len(online_memories) > 5:
            output += f"\n... 还有 {len(online_memories) - 5} 条记忆\n"
    else:
        output += "无\n"
    output += "\n"

    # 4. 对话历史
    output += "#### 💬 对话历史\n\n"
    conv_history = ctx.get("conversation_history", [])
    if conv_history:
        output += f"共 {len(conv_history)} 条消息:\n\n"
        for i, msg in enumerate(conv_history[-3:], 1):  # 只显示最近3条
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            output += f"{i}. **{role}**: {content}\n"
    else:
        output += "无\n"
    output += "\n"

    # 5. 统计信息
    output += "#### 📊 统计信息\n\n"
    output += f"- System Prompt 长度: {ctx.get('system_prompt_length', 0)} 字符\n"
    output += f"- 总消息数: {ctx.get('total_messages', 0)}\n"

    return output


class ChatbotGUI:
    """Gradio 聊天机器人 GUI"""

    def __init__(self):
        self.session_id = str(uuid4())
        self.message_count = 0

    async def process_message(
        self,
        message: str,
        history: List[Tuple[str, str]],
        progress=gr.Progress()
    ) -> Tuple[List[Tuple[str, str]], str]:
        """
        处理用户消息

        Args:
            message: 用户输入
            history: 对话历史
            progress: Gradio 进度条

        Returns:
            (更新后的历史, 空字符串)
        """
        if not message.strip():
            return history, ""

        try:
            async for db in get_db():
                agent = MemoryDrivenAgent(db, use_reasoner=False)

                # 初始化进度
                progress(0, desc="🔄 开始处理...")

                response = await agent.process_message(
                    user_message=message,
                    session_id=self.session_id,
                    progress_callback=progress
                )

                await db.commit()

                if response["success"]:
                    response_text = response["text"]
                else:
                    response_text = f"❌ 错误: {response.get('error', '未知错误')}"

                # 更新历史
                history.append((message, response_text))
                self.message_count += 1

                return history, ""

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ 错误详情:\n{error_detail}")
            error_msg = f"❌ 处理消息时出错: {str(e)}"
            history.append((message, error_msg))
            return history, ""

    def clear_chat(self) -> Tuple[List, str]:
        """清除对话"""
        self.session_id = str(uuid4())
        self.message_count = 0
        return [], f"会话已重置\n新会话 ID: {self.session_id[:8]}..."

    def get_session_info(self) -> str:
        """获取会话信息"""
        return f"""
### 📊 会话信息

- **会话 ID**: `{self.session_id[:8]}...`
- **消息数**: {self.message_count}
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def create_interface():
    """创建 Gradio 界面"""
    chatbot_gui = ChatbotGUI()

    with gr.Blocks(
        title="GauzAssist Chat",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown("# 💬 GauzAssist Chat")
        gr.Markdown("基于记忆驱动的智能助手 - Gradio 版本")

        with gr.Tabs():
            # 标签页 1: 聊天界面
            with gr.Tab("💬 聊天"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="对话",
                            height=400,
                            show_copy_button=True,
                            type="tuples"
                        )

                        # 实时进度显示区域
                        active_progress_display = gr.Markdown(
                            value="",
                            visible=True,
                            label="处理进度"
                        )

                        with gr.Row():
                            msg = gr.Textbox(
                                label="输入消息",
                                placeholder="输入消息...",
                                lines=2,
                                scale=4
                            )
                            submit_btn = gr.Button("发送", variant="primary", scale=1)

                        clear_btn = gr.Button("🗑️ 清除对话", variant="secondary")

                    with gr.Column(scale=1):
                        session_info = gr.Markdown(chatbot_gui.get_session_info())

                        gr.Markdown("### ⚙️ 设置")
                        gr.Markdown("更多设置即将推出...")

            # 标签页 2: 仪表盘
            with gr.Tab("📊 仪表盘"):
                # 活跃请求区域
                gr.Markdown("## 🔄 正在进行的请求")
                active_requests_display = gr.Markdown(
                    value=format_active_progress()[1],  # 只取 dashboard 部分
                    label="实时进度"
                )

                gr.Markdown("---")

                # 历史请求区域
                gr.Markdown("## 📜 历史请求")
                performance_display = gr.Markdown(
                    value=format_performance_data(),
                    label="性能追踪"
                )

                with gr.Row():
                    refresh_btn = gr.Button("🔄 刷新数据", variant="primary")
                    clear_history_btn = gr.Button("🗑️ 清除历史", variant="secondary")

                gr.Markdown("---")

                # 上下文内容区域
                gr.Markdown("## 📝 上下文内容")
                context_display = gr.Markdown(
                    value=format_context_content(),
                    label="上下文内容"
                )

                refresh_context_btn = gr.Button("🔄 刷新上下文", variant="primary")

                gr.Markdown("### 📈 功能说明")
                gr.Markdown("""
                - **主流程**: 同步执行的步骤，按顺序完成
                - **后台任务**: 异步执行的步骤，不阻塞主流程
                - 每个请求都会记录各步骤的耗时，帮助定位性能瓶颈
                """)

        # 定时器：每 2 秒刷新一次进度
        timer = gr.Timer(value=2, active=True)
        timer.tick(
            fn=format_active_progress,
            outputs=[active_progress_display, active_requests_display]
        )

        # 事件绑定
        submit_btn.click(
            fn=chatbot_gui.process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )

        msg.submit(
            fn=chatbot_gui.process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )

        clear_btn.click(
            fn=chatbot_gui.clear_chat,
            outputs=[chatbot, session_info]
        )

        # Dashboard 事件绑定
        refresh_btn.click(
            fn=format_performance_data,
            outputs=performance_display
        )

        def clear_performance_history():
            PerformanceTracker.clear_history()
            return format_performance_data()

        clear_history_btn.click(
            fn=clear_performance_history,
            outputs=performance_display
        )

        refresh_context_btn.click(
            fn=format_context_content,
            outputs=context_display
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
