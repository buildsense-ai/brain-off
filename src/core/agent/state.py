"""
Agent state management for conversation context.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
    tool_calls: Optional[List[Dict[str, Any]]] = None  # Only for assistant messages
    tool_call_id: Optional[str] = None  # Only for tool messages


@dataclass
class AgentState:
    """
    Agent state for managing conversation context.

    This is stored in-memory for now. In Phase 9, we can add Redis persistence.
    """
    session_id: UUID = field(default_factory=uuid4)
    conversation_history: List[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to conversation history."""
        message = Message(role=role, content=content, **kwargs)
        self.conversation_history.append(message)

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages from conversation history."""
        return self.conversation_history[-limit:]


class SessionManager:
    """
    Manages agent sessions in-memory.

    In Phase 9, this can be upgraded to use Redis for persistence.
    """

    def __init__(self):
        self._sessions: Dict[UUID, AgentState] = {}

    def create_session(self) -> AgentState:
        """Create a new agent session."""
        state = AgentState()
        self._sessions[state.session_id] = state
        return state

    def get_session(self, session_id: UUID) -> Optional[AgentState]:
        """Get an existing session by ID."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: UUID) -> None:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def list_sessions(self) -> List[UUID]:
        """List all active session IDs."""
        return list(self._sessions.keys())


# Global session manager instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return _session_manager
