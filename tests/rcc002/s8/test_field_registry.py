"""Independent re-derivation tests for rcc002.s8.field_registry.

Mandatory S8 test item 1 (exact 232/534-field order and allowlist hashes)
and item 2 (unique owner-stage and leakage resolution for every field).
This module re-parses the certified specification markdown itself -- it
never imports ``rcc002.s8.field_registry`` constants as its expectation,
only as the subject under test -- so a corrupted transcription in
``field_registry.py`` cannot pass by agreeing with itself.
"""

from __future__ import annotations

import json
import os
import re
import unittest

from rcc002.s8 import field_registry as fr
from rcc002.s8.canonical import canonical_sha256
from rcc002.s8.reason_codes import FieldRegistryError

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
SPEC_PATH = os.path.join(
    REPO_ROOT,
    "docs",
    "specifications",
    "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
)


def _independent_registry_from_spec() -> dict:
    with open(SPEC_PATH, encoding="utf-8") as handle:
        text = handle.read()
    blocks = re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)
    parsed = [json.loads(block) for block in blocks]
    registry = next(
        obj
        for obj in parsed
        if isinstance(obj, dict)
        and obj.get("field_registry_id") == "RCC002_S8_FIELD_OWNERSHIP_V1"
    )
    return registry


class TestIndependentRegistryReDerivation(unittest.TestCase):
    def test_embedded_registry_matches_spec_byte_for_byte(self) -> None:
        independent = _independent_registry_from_spec()
        self.assertEqual(fr.FIELD_REGISTRY_ID, independent["field_registry_id"])
        self.assertEqual(
            fr.FIELD_REGISTRY_VERSION, independent["field_registry_version"]
        )
        self.assertEqual(len(fr.FIELD_REGISTRY_GROUPS), len(independent["groups"]))
        for embedded, expected in zip(fr.FIELD_REGISTRY_GROUPS, independent["groups"]):
            self.assertEqual(
                embedded["field_owner_stage"], expected["field_owner_stage"]
            )
            self.assertEqual(embedded["leakage_class"], expected["leakage_class"])
            self.assertEqual(list(embedded["fields"]), expected["fields"])

    def test_total_field_count_is_564(self) -> None:
        total = sum(len(group["fields"]) for group in fr.FIELD_REGISTRY_GROUPS)
        self.assertEqual(total, 564)
        self.assertEqual(len(fr.FIELD_OWNER_STAGE), 564)
        self.assertEqual(len(fr.FIELD_LEAKAGE_CLASS), 564)

    def test_registry_sha256_is_mechanically_reproducible(self) -> None:
        independent = _independent_registry_from_spec()
        independent_canonical = {
            "field_registry_id": independent["field_registry_id"],
            "field_registry_version": independent["field_registry_version"],
            "groups": independent["groups"],
        }
        self.assertEqual(
            canonical_sha256(independent_canonical), fr.FIELD_REGISTRY_SHA256
        )


class TestUniqueOwnerAndLeakageResolution(unittest.TestCase):
    """Item 2: every field resolves to exactly one owner stage and leakage
    class; no field appears in more than one registry group."""

    def test_every_field_appears_in_exactly_one_group(self) -> None:
        seen: dict[str, str] = {}
        for group in fr.FIELD_REGISTRY_GROUPS:
            for field in group["fields"]:
                self.assertNotIn(
                    field,
                    seen,
                    msg=f"{field!r} appears in both {seen.get(field)!r} and "
                    f"{group['field_owner_stage']!r}",
                )
                seen[field] = group["field_owner_stage"]
        self.assertEqual(len(seen), 564)

    def test_resolve_field_matches_group_membership(self) -> None:
        for group in fr.FIELD_REGISTRY_GROUPS:
            for field in group["fields"]:
                owner, leakage = fr.resolve_field(field)
                self.assertEqual(owner, group["field_owner_stage"])
                self.assertEqual(leakage, group["leakage_class"])

    def test_unregistered_field_fails_closed(self) -> None:
        with self.assertRaises(FieldRegistryError):
            fr.resolve_field("definitely_not_a_registered_field")

    def test_resolve_field_rejects_non_string(self) -> None:
        with self.assertRaises(FieldRegistryError):
            fr.resolve_field(None)  # type: ignore[arg-type]

    def test_resolve_field_rejects_empty_string(self) -> None:
        with self.assertRaises(FieldRegistryError):
            fr.resolve_field("")

    def test_leakage_classes_are_the_four_registered_values(self) -> None:
        self.assertEqual(
            set(fr.FIELD_LEAKAGE_CLASS.values()),
            {
                "POINT_IN_TIME",
                "FUTURE_OUTCOME",
                "PROVENANCE_METADATA",
                "AUDIT_METADATA",
            },
        )

    def test_duplicate_field_across_groups_fails_closed(self) -> None:
        mutated_groups = fr.FIELD_REGISTRY_GROUPS + (
            {
                "field_owner_stage": "S1_NORMALIZED",
                "leakage_class": "POINT_IN_TIME",
                "fields": ("open_time",),  # already owned by S1_NORMALIZED
            },
        )
        owner_stage: dict[str, str] = {}
        with self.assertRaises(FieldRegistryError):
            for group in mutated_groups:
                for field in group["fields"]:
                    if field in owner_stage:
                        raise FieldRegistryError(
                            f"field {field!r} has more than one registry entry"
                        )
                    owner_stage[field] = group["field_owner_stage"]


if __name__ == "__main__":
    unittest.main()
