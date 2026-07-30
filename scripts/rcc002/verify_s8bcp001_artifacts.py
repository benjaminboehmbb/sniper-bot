#!/usr/bin/env python3
"""Mechanical verification for RCC-002 S8BCP-001 Revision 2 artifacts."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


EXPECTED_SPECIFICATIONS = {
    "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md": "0.8.0",
    "RCC_002_DATA_VALIDATION_2026-07-23.md": "0.6.0",
    "RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md": "0.4.3",
    "RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md": "0.4.2",
    "RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md": "0.5.1",
    "RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md": "0.5.0",
    "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md": "0.8.0",
}
MANIFEST_TYPES = (
    "source-manifest",
    "stage-manifest",
    "run-manifest",
    "dataset-manifest",
    "review-manifest",
    "reproduction-manifest",
)


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def find_json_block(text: str, heading_pattern: str) -> dict:
    match = re.search(
        heading_pattern + r".*?```json\n(.*?)\n```",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"JSON block not found: {heading_pattern}")
    return json.loads(match.group(1))


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    specification_root = repo / "docs/specifications"
    schema_root = repo / "schemas/rcc002/manifests"
    fixture_root = repo / "tests/fixtures/rcc002/manifests"

    json_files = sorted(repo.rglob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    for name, version in EXPECTED_SPECIFICATIONS.items():
        text = (specification_root / name).read_text(encoding="utf-8")
        assert re.search(
            rf"^\| Version \| `?{re.escape(version)}`? \|$",
            text,
            flags=re.MULTILINE,
        )
        assert "S8BCP-001 Revision 2 Corrected Candidate" in text

    for manifest_type in MANIFEST_TYPES:
        schema_path = schema_root / manifest_type / "1.0.0.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"] == f"urn:rcc002:schema:{manifest_type}:1.0.0"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"]
        assert schema["properties"]
        positive = sorted((fixture_root / manifest_type / "1.0.0").glob("*-valid.json"))
        negative = sorted(
            (fixture_root / manifest_type / "1.0.0/negative").glob("*.json")
        )
        assert len(positive) == 2
        assert len(negative) == 11

    class_registry = json.loads(
        (
            repo
            / "registries/rcc002/release/release_artifact_class_registry.v1.json"
        ).read_text(encoding="utf-8")
    )
    rules = class_registry["correction_bundle_path_rules"]
    class_counts: dict[str, int] = {}
    for path in sorted(item for item in repo.rglob("*") if item.is_file()):
        relative = path.relative_to(repo).as_posix()
        matches = [
            rule["artifact_class"]
            for rule in rules
            if (
                ("path_prefix" in rule and relative.startswith(rule["path_prefix"]))
                or ("exact_path" in rule and relative == rule["exact_path"])
            )
        ]
        assert len(matches) == 1, (relative, matches)
        class_counts[matches[0]] = class_counts.get(matches[0], 0) + 1

    dp_text = (
        specification_root / "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md"
    ).read_text(encoding="utf-8")
    registry = find_json_block(dp_text, r"^#### 7\.9\.1 ")
    owners: dict[str, tuple[str, str]] = {}
    for group in registry["groups"]:
        for field in group["fields"]:
            assert field not in owners
            owners[field] = (
                group["field_owner_stage"],
                group["leakage_class"],
            )

    views: list[tuple[str, dict]] = []
    for index in range(1, 7):
        pattern = rf"^##### 7\.9\.3\.{index} `([^`]+)`"
        heading = re.search(pattern, dp_text, flags=re.MULTILINE)
        assert heading is not None
        view = find_json_block(dp_text, re.escape(heading.group(0)))
        preimage = {
            "allowed_producer_stages": view["allowed_producer_stages"],
            "fields": [
                {
                    "field_name": field,
                    "field_owner_stage": owners[field][0],
                    "leakage_class": owners[field][1],
                }
                for field in view["fields"]
            ],
        }
        assert sha256(canonical_json(preimage)).hexdigest() == view["allowlist_sha256"]
        views.append((heading.group(1), view))

    label = views[4][1]
    audit = views[5][1]
    assert audit["schema_ref"] == "rcc002.view.audit/2.0.0"
    assert audit["fields"] == label["fields"]
    assert audit["allowed_producer_stages"] == label["allowed_producer_stages"]
    assert len(audit["fields"]) == 534
    assert audit["allowlist_sha256"] == (
        "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"
    )

    identity_fixture = json.loads(
        (
            repo
            / "tests/fixtures/rcc002/source/source_identity_golden.v1.json"
        ).read_text(encoding="utf-8")
    )
    source_case = identity_fixture["source_snapshot_case"]
    source_digest = sha256(canonical_json(source_case["preimage"])).hexdigest()
    assert source_digest == source_case["expected_sha256"]
    assert "source:sha256:" + source_digest == source_case[
        "expected_source_snapshot_id"
    ]
    for row in identity_fixture["source_row_id_cases"]:
        expected = (
            "RCC002_S1_SOURCE_ROW_ID_V2:"
            f"{source_case['expected_source_snapshot_id']}:"
            f"{row['source_file_ordinal']:08d}:"
            f"{row['original_record_index']:020d}"
        )
        assert expected == row["expected_source_row_id"]

    for path in sorted(repo.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert text.count("```") % 2 == 0
        assert text.endswith("\n")
        assert all(
            not line.endswith((" ", "\t"))
            for line in text.splitlines()
        )

    for path in sorted(repo.rglob("*.py")):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    print(
        json.dumps(
            {
                "result": "PASS",
                "json_files": len(json_files),
                "manifest_schemas": len(MANIFEST_TYPES),
                "manifest_positive_fixtures": 12,
                "manifest_negative_fixtures": 66,
                "audit_v2_fields": len(audit["fields"]),
                "source_identity_golden_sha256": source_digest,
                "correction_bundle_class_counts": class_counts,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
