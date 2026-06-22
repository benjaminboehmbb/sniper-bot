from __future__ import annotations

import csv
import json
from pathlib import Path

from tools.ssi.common.scientific_artifacts import ScientificArtifacts
from tools.ssi.common.scientific_persistence import ScientificPersistence


class StateAnalyticsArtifactPersistence(ScientificPersistence):
    def persist(
        self,
        artifacts: ScientificArtifacts,
        output_dir: Path,
    ) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        written_paths: list[Path] = []

        for artifact in artifacts.csv_artifacts:
            path = output_dir / artifact.filename
            with path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(artifact.header)
                writer.writerows(artifact.rows)
            written_paths.append(path)

        for artifact in artifacts.text_artifacts:
            path = output_dir / artifact.filename
            path.write_text(artifact.content, encoding="utf-8")
            written_paths.append(path)

        for artifact in artifacts.json_artifacts:
            path = output_dir / artifact.filename
            path.write_text(
                json.dumps(artifact.content, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            written_paths.append(path)

        return written_paths