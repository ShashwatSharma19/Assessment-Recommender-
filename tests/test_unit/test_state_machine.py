"""Unit tests for state machine."""

import pytest
from app.state import ConversationStateMachine, ConversationState, GatheredContext


class TestGatheredContext:
    """Tests for GatheredContext."""

    def test_empty_context_not_sufficient(self):
        """Test that empty context is not sufficient for recommendation."""
        context = GatheredContext()
        assert not context.is_sufficient_for_recommendation()

    def test_role_makes_sufficient(self):
        """Test that role alone makes context sufficient."""
        context = GatheredContext(role="Java Developer")
        assert context.is_sufficient_for_recommendation()

    def test_domain_makes_sufficient(self):
        """Test that domain makes context sufficient."""
        context = GatheredContext(domains=["Technical"])
        assert context.is_sufficient_for_recommendation()

    def test_test_type_makes_sufficient(self):
        """Test that test type preference makes context sufficient."""
        context = GatheredContext(test_type_preference=["K", "C"])
        assert context.is_sufficient_for_recommendation()

    def test_update_from_dict(self):
        """Test updating context from dictionary."""
        context = GatheredContext()
        context.update_from_dict({
            "role": "Manager",
            "seniority": "Senior",
            "domains": ["Behavioral", "Leadership"],
        })
        assert context.role == "Manager"
        assert context.seniority == "Senior"
        assert context.domains == ["Behavioral", "Leadership"]


class TestStateMachine:
    """Tests for ConversationStateMachine."""

    @pytest.fixture
    def state_machine(self):
        """Create a state machine instance."""
        return ConversationStateMachine(max_turns=8)

    def test_initial_state(self, state_machine):
        """Test initial state is GATHERING_CONTEXT."""
        assert state_machine.get_state() == ConversationState.GATHERING_CONTEXT

    def test_turn_counting(self, state_machine):
        """Test turn counting."""
        assert state_machine.get_turn_count() == 0

        state_machine.add_turn("user", "Hello")
        assert state_machine.get_turn_count() == 1

        state_machine.add_turn("assistant", "Hi")
        assert state_machine.get_turn_count() == 1  # Still 1, assistant doesn't count

        state_machine.add_turn("user", "Help me")
        assert state_machine.get_turn_count() == 2

    def test_has_turns_remaining(self, state_machine):
        """Test turn availability."""
        assert state_machine.has_turns_remaining()

        # Fill up turns
        for i in range(8):
            state_machine.add_turn("user", f"Turn {i+1}")

        assert not state_machine.has_turns_remaining()

    def test_valid_state_transition(self, state_machine):
        """Test valid state transitions."""
        # From GATHERING -> READY_TO_RECOMMEND
        assert state_machine.can_transition_to(ConversationState.READY_TO_RECOMMEND)
        assert state_machine.transition_to(ConversationState.READY_TO_RECOMMEND)
        assert state_machine.get_state() == ConversationState.READY_TO_RECOMMEND

    def test_invalid_state_transition(self, state_machine):
        """Test that invalid transitions are rejected."""
        state_machine.state = ConversationState.DONE
        # Can't transition away from DONE
        assert not state_machine.can_transition_to(ConversationState.GATHERING_CONTEXT)

    def test_turn_limit_blocks_transition(self, state_machine):
        """Test that exceeding turn limit blocks transitions."""
        state_machine.turn_count = state_machine.max_turns
        state_machine.state = ConversationState.GATHERING_CONTEXT

        # Can't transition to READY_TO_RECOMMEND if at max turns
        assert not state_machine.can_transition_to(ConversationState.READY_TO_RECOMMEND)

        # Can transition to DONE
        assert state_machine.can_transition_to(ConversationState.DONE)

    def test_context_update_triggers_transition(self, state_machine):
        """Test that sufficient context triggers auto-transition."""
        assert state_machine.get_state() == ConversationState.GATHERING_CONTEXT

        state_machine.update_context({"role": "Java Developer"})

        assert state_machine.get_state() == ConversationState.READY_TO_RECOMMEND

    def test_should_clarify(self, state_machine):
        """Test clarification detection."""
        assert state_machine.should_clarify()

        state_machine.update_context({"role": "Manager"})
        assert not state_machine.should_clarify()

    def test_should_recommend(self, state_machine):
        """Test recommendation detection."""
        assert not state_machine.should_recommend()

        state_machine.transition_to(ConversationState.READY_TO_RECOMMEND)
        assert state_machine.should_recommend()

    def test_recommendations_management(self, state_machine):
        """Test setting and getting recommendations."""
        assert state_machine.get_recommendations() is None

        recs = [
            {"name": "Java 8", "url": "https://www.shl.com/java/"},
            {"name": "OPQ32r", "url": "https://www.shl.com/opq/"},
        ]
        state_machine.set_recommendations(recs)

        assert state_machine.get_recommendations() == recs

    def test_reset(self, state_machine):
        """Test resetting state machine."""
        state_machine.add_turn("user", "Hello")
        state_machine.update_context({"role": "Manager"})
        state_machine.set_recommendations([{"name": "Test"}])

        state_machine.reset()

        assert state_machine.get_state() == ConversationState.GATHERING_CONTEXT
        assert state_machine.get_turn_count() == 0
        assert state_machine.get_recommendations() is None
        assert len(state_machine.conversation_history) == 0

    def test_get_state_info(self, state_machine):
        """Test getting complete state information."""
        state_machine.update_context({"role": "Manager", "domains": ["Leadership"]})

        info = state_machine.get_state_info()

        assert info["current_state"] == ConversationState.READY_TO_RECOMMEND.value
        assert info["turn_count"] == 0
        assert info["has_turns_remaining"] is True
        assert info["gathered_context"]["role"] == "Manager"
        assert info["gathered_context"]["domains"] == ["Leadership"]

    def test_refine_recommendations(self, state_machine):
        """Test refining recommendations."""
        initial_recs = [
            {"name": "Java 8", "url": "https://www.shl.com/java/"},
            {"name": "OPQ32r", "url": "https://www.shl.com/opq/"},
        ]
        state_machine.set_recommendations(initial_recs)
        state_machine.transition_to(ConversationState.READY_TO_RECOMMEND)

        # Refine with additional context
        refined = state_machine.refine_recommendations({"test_type_preference": "P"})

        assert refined is not None

    def test_conversation_flow_vague_to_recommendation(self, state_machine):
        """Test complete conversation flow from vague query to recommendation."""
        # Initial state
        assert state_machine.should_clarify()
        state_machine.add_turn("user", "I need an assessment for hiring")

        # Clarify
        state_machine.add_turn("assistant", "What role are you hiring for?")
        state_machine.add_turn("user", "Java developer")

        # Update context and auto-transition
        state_machine.update_context({"role": "Java Developer"})
        assert state_machine.should_recommend()

        # Set recommendations
        recs = [{"name": "Java 8", "url": "https://www.shl.com/java/"}]
        state_machine.set_recommendations(recs)
        state_machine.add_turn("assistant", "I recommend Java 8")

        # Complete
        state_machine.transition_to(ConversationState.DONE)
        assert state_machine.is_done()
