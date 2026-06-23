from __future__ import annotations

from pathlib import Path
from typing import Any


class DecisionEvidencePersistence:
    """
    Persists Decision Evidence artifacts to disk.
    """

    def persist(
        self,
        artifacts: dict[str, Any],
        output_dir: Path,
    ) -> None:
        """
        Persist all rendered artifacts.
        """

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for filename, content in artifacts.items():

            path = output_dir / filename

            path.write_text(
                content,
                encoding="utf-8",
            )