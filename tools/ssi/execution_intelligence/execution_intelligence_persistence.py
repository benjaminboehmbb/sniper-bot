from __future__ import annotations

from pathlib import Path
from typing import Any


class ExecutionIntelligencePersistence:
    """
    Persists Execution Intelligence artifacts to disk.
    """

    def persist(
        self,
        artifacts: dict[str, Any],
        output_dir: Path,
    ) -> list[Path]:
        """
        Persist all rendered artifacts and return written paths.
        """

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        written_paths: list[Path] = []

        for filename, content in artifacts.items():
            path = output_dir / filename

            path.write_text(
                content,
                encoding="utf-8",
            )

            written_paths.append(path)

        return written_paths