from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import List

from tools.ssi.builder.trade_state_vector import TradeStateVector


def _avg(values: List[float]) -> float:
    if not values:
        return 0.0
    return mean(values)


def build_tsv_summary(
    *,
    records: List[TradeStateVector],
    runtime_id: str,
    csv_output_path: Path,
    manifest_output_path: Path,
) -> str:
    if not records:
        raise ValueError("records must not be empty")

    dimensions = {
        "progress": [record.progress for record in records],
        "compatibility": [record.compatibility for record in records],
        "stability": [record.stability for record in records],
        "confidence": [record.confidence for record in records],
    }

    trade_ids = sorted({record.trade_id for record in records if record.trade_id})
    sides = sorted({record.side for record in records})
    versions = sorted({record.tsv_version for record in records})
    generators = sorted({record.generator_name for record in records})

    lines = [
        "# TSV DATASET SUMMARY",
        "",
        "Runtime ID:",
        runtime_id,
        "",
        "Status:",
        "GENERATED",
        "",
        "TSV Count:",
        str(len(records)),
        "",
        "Trade Count:",
        str(len(trade_ids)),
        "",
        "Sides:",
        ", ".join(sides),
        "",
        "TSV Versions:",
        ", ".join(versions),
        "",
        "Generators:",
        ", ".join(generators),
        "",
        "CSV Output:",
        str(csv_output_path),
        "",
        "Manifest Output:",
        str(manifest_output_path),
        "",
        "---",
        "",
        "# Dimension Averages",
        "",
    ]

    for name, values in dimensions.items():
        lines.extend(
            [
                f"## {name}",
                "",
                f"min: {min(values):.6f}",
                "",
                f"max: {max(values):.6f}",
                "",
                f"mean: {_avg(values):.6f}",
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "# Scientific Note",
            "",
            "This summary describes the generated TSV dataset only.",
            "",
            "It does not contain execution decisions, trade recommendations, or adaptive behavior.",
            "",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def write_tsv_summary(
    *,
    records: List[TradeStateVector],
    runtime_id: str,
    csv_output_path: Path,
    manifest_output_path: Path,
    summary_output_path: Path,
) -> Path:
    summary_output_path.parent.mkdir(parents=True, exist_ok=True)
    text = build_tsv_summary(
        records=records,
        runtime_id=runtime_id,
        csv_output_path=csv_output_path,
        manifest_output_path=manifest_output_path,
    )
    summary_output_path.write_text(text, encoding="utf-8")
    return summary_output_path
