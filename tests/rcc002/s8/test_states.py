"""Tests for rcc002.s8.states.

Mandatory S8 test item 14: failed or quarantined publication prevention.
"""

from __future__ import annotations

import unittest

from rcc002.s8.reason_codes import PublicationStateError
from rcc002.s8.states import (
    BuildState,
    require_not_diagnostic_only,
    require_publishable,
    validate_transition,
)


class TestTransitions(unittest.TestCase):
    def test_normal_success_path_is_permitted(self) -> None:
        validate_transition(BuildState.PLANNED, BuildState.RUNNING)
        validate_transition(BuildState.RUNNING, BuildState.VALIDATING)
        validate_transition(BuildState.VALIDATING, BuildState.CANDIDATE)
        validate_transition(BuildState.CANDIDATE, BuildState.PUBLISHED)
        validate_transition(BuildState.PUBLISHED, BuildState.SUPERSEDED)

    def test_failed_and_quarantined_are_terminal(self) -> None:
        for target in BuildState:
            with self.subTest(target=target.value):
                with self.assertRaises(PublicationStateError):
                    validate_transition(BuildState.FAILED, target)
                with self.assertRaises(PublicationStateError):
                    validate_transition(BuildState.QUARANTINED, target)

    def test_cannot_skip_straight_to_published(self) -> None:
        with self.assertRaises(PublicationStateError):
            validate_transition(BuildState.PLANNED, BuildState.PUBLISHED)
        with self.assertRaises(PublicationStateError):
            validate_transition(BuildState.RUNNING, BuildState.PUBLISHED)

    def test_string_states_accepted(self) -> None:
        validate_transition("planned", "running")

    def test_unknown_state_rejected(self) -> None:
        with self.assertRaises(PublicationStateError):
            validate_transition("planned", "not-a-real-state")


class TestPublicationPrevention(unittest.TestCase):
    """Item 14: only CANDIDATE may publish; FAILED/QUARANTINED never may."""

    def test_only_candidate_is_publishable(self) -> None:
        require_publishable(BuildState.CANDIDATE)

    def test_every_other_state_is_not_publishable(self) -> None:
        for state in BuildState:
            if state is BuildState.CANDIDATE:
                continue
            with self.subTest(state=state.value):
                with self.assertRaises(PublicationStateError):
                    require_publishable(state)

    def test_failed_publication_explicitly_rejected(self) -> None:
        with self.assertRaises(PublicationStateError):
            require_publishable(BuildState.FAILED)

    def test_quarantined_publication_explicitly_rejected(self) -> None:
        with self.assertRaises(PublicationStateError):
            require_publishable(BuildState.QUARANTINED)

    def test_diagnostic_only_states_rejected_from_final_path(self) -> None:
        for state in (BuildState.FAILED, BuildState.QUARANTINED):
            with self.subTest(state=state.value):
                with self.assertRaises(PublicationStateError):
                    require_not_diagnostic_only(state, context="release manifest")

    def test_non_diagnostic_states_permitted_on_final_path(self) -> None:
        for state in (BuildState.PUBLISHED, BuildState.SUPERSEDED, BuildState.WITHDRAWN):
            with self.subTest(state=state.value):
                require_not_diagnostic_only(state, context="release manifest")


if __name__ == "__main__":
    unittest.main()
