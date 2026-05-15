"""Explicit state machine for conversation flow."""

from enum import Enum
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


class ConversationState(str, Enum):
    """States in the conversation flow."""
    GATHERING_CONTEXT = "gathering_context"
    READY_TO_RECOMMEND = "ready_to_recommend"
    COMPARING = "comparing"
    DONE = "done"


@dataclass
class GatheredContext:
    """Information gathered during clarification phase."""
    role: Optional[str] = None
    seniority: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    test_type_preference: List[str] = field(default_factory=list)  # K, C, P
    additional_requirements: Optional[str] = None

    def is_sufficient_for_recommendation(self) -> bool:
        """Check if we have enough context to make recommendations."""
        # Need at least role or domain information
        return bool(self.role or self.domains or self.test_type_preference)

    def update_from_dict(self, data: Dict[str, Any]):
        """Update context from a dictionary."""
        if 'role' in data:
            self.role = data['role']
        if 'seniority' in data:
            self.seniority = data['seniority']
        if 'domains' in data:
            if isinstance(data['domains'], list):
                self.domains = data['domains']
            elif isinstance(data['domains'], str):
                self.domains = [data['domains']]
        if 'test_type_preference' in data:
            if isinstance(data['test_type_preference'], list):
                self.test_type_preference = data['test_type_preference']
            elif isinstance(data['test_type_preference'], str):
                self.test_type_preference = [data['test_type_preference']]
        if 'additional_requirements' in data:
            self.additional_requirements = data['additional_requirements']


class ConversationStateMachine:
    """Manages conversation state and transitions."""

    def __init__(self, max_turns: int = 8):
        """Initialize state machine."""
        self.state = ConversationState.GATHERING_CONTEXT
        self.gathered_context = GatheredContext()
        self.turn_count = 0
        self.max_turns = max_turns
        self.conversation_history: List[Dict[str, str]] = []
        self.last_recommendations: Optional[List[Dict[str, Any]]] = None

    def get_state(self) -> ConversationState:
        """Get current state."""
        return self.state

    def add_turn(self, role: str, content: str):
        """Add a turn to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        if role == "user":
            self.turn_count += 1

    def get_turn_count(self) -> int:
        """Get the current turn count (user turns only)."""
        return self.turn_count

    def has_turns_remaining(self) -> bool:
        """Check if we have turns remaining."""
        return self.turn_count < self.max_turns

    def can_transition_to(self, new_state: ConversationState) -> bool:
        """Check if transition is allowed."""
        # Can't transition if at max turns
        if not self.has_turns_remaining() and new_state != ConversationState.DONE:
            return False

        # Validate state transitions
        valid_transitions = {
            ConversationState.GATHERING_CONTEXT: [
                ConversationState.READY_TO_RECOMMEND,
                ConversationState.COMPARING,
                ConversationState.DONE,
            ],
            ConversationState.READY_TO_RECOMMEND: [
                ConversationState.GATHERING_CONTEXT,  # Refine
                ConversationState.COMPARING,
                ConversationState.DONE,
            ],
            ConversationState.COMPARING: [
                ConversationState.READY_TO_RECOMMEND,
                ConversationState.GATHERING_CONTEXT,
                ConversationState.DONE,
            ],
            ConversationState.DONE: [],
        }

        allowed = valid_transitions.get(self.state, [])
        return new_state in allowed

    def transition_to(self, new_state: ConversationState) -> bool:
        """Transition to a new state."""
        if not self.can_transition_to(new_state):
            return False

        self.state = new_state
        return True

    def update_context(self, data: Dict[str, Any]) -> bool:
        """Update gathered context."""
        try:
            self.gathered_context.update_from_dict(data)

            # Auto-transition to ready if we have sufficient context
            if self.state == ConversationState.GATHERING_CONTEXT:
                if self.gathered_context.is_sufficient_for_recommendation():
                    self.transition_to(ConversationState.READY_TO_RECOMMEND)

            return True
        except Exception:
            return False

    def should_clarify(self) -> bool:
        """Check if we should ask clarification questions."""
        return self.state == ConversationState.GATHERING_CONTEXT and \
               not self.gathered_context.is_sufficient_for_recommendation()

    def should_recommend(self) -> bool:
        """Check if we should provide recommendations."""
        return self.state == ConversationState.READY_TO_RECOMMEND

    def should_compare(self) -> bool:
        """Check if we're in comparison mode."""
        return self.state == ConversationState.COMPARING

    def is_done(self) -> bool:
        """Check if conversation is done."""
        return self.state == ConversationState.DONE

    def set_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Set the recommendations to return."""
        self.last_recommendations = recommendations

    def get_recommendations(self) -> Optional[List[Dict[str, Any]]]:
        """Get current recommendations."""
        return self.last_recommendations

    def refine_recommendations(self, data: Dict[str, Any]):
        """Refine existing recommendations based on new criteria."""
        # Update context (may change gathered_context)
        self.update_context(data)

        # Re-rank based on new context
        if self.last_recommendations:
            # Could add re-ranking logic here based on updated context
            pass

        return self.last_recommendations

    def reset(self):
        """Reset state machine for new conversation."""
        self.state = ConversationState.GATHERING_CONTEXT
        self.gathered_context = GatheredContext()
        self.turn_count = 0
        self.conversation_history = []
        self.last_recommendations = None

    def get_state_info(self) -> Dict[str, Any]:
        """Get detailed state information."""
        return {
            "current_state": self.state.value,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "has_turns_remaining": self.has_turns_remaining(),
            "gathered_context": {
                "role": self.gathered_context.role,
                "seniority": self.gathered_context.seniority,
                "domains": self.gathered_context.domains,
                "test_type_preference": self.gathered_context.test_type_preference,
                "additional_requirements": self.gathered_context.additional_requirements,
            },
            "has_recommendations": self.last_recommendations is not None,
        }
