"""Pre-Generation Verifier ensuring dataset integrity before generating RecoverScene.cs."""
import logging
from pathlib import Path
from typing import Any

from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


class PreGenerationVerifier:
    """Validates scene dataset invariants before C# Editor script generation."""

    def __init__(self, registry: PathIDRegistry, reports_dir: Path | str):
        self.registry = registry
        self.reports_dir = Path(reports_dir)

    def verify_and_report(self) -> bool:
        """Emits verification report and raises ValueError if critical gameplay objects are missing."""
        gos = [o for o in self.registry.all_objects if o.type_name == "GameObject"]
        mbs = [o for o in self.registry.all_objects if o.type_name == "MonoBehaviour"]

        # Find key GameObjects
        go_names = {o.name for o in gos}
        has_player = "player" in go_names
        has_camera = "Main Camera" in go_names
        has_gamemanager = "GameManager" in go_names

        # Custom scripts attached
        custom_script_count = 0
        custom_scripts_found = set()
        for mb in mbs:
            script_pptr = mb.properties.get("m_Script", {})
            sc_name = script_pptr.get("Name", mb.name)
            if sc_name and sc_name not in ("MonoBehaviour", "Unknown"):
                custom_script_count += 1
                custom_scripts_found.add(sc_name)

        has_player_movement = "PlayerMovement" in custom_scripts_found

        # Generate Verification Table Report
        report_lines = [
            "# Dataset Integrity Pre-Generation Verification Report",
            "",
            "| Metric | Expected Minimum | Found | Status |",
            "|---|---|---|---|",
            f"| `GameObjects` | 320 | **{len(gos)}** | {'PASS' if len(gos) >= 320 else 'FAIL'} |",
            f"| `MonoBehaviours` | 16 | **{len(mbs)}** | {'PASS' if len(mbs) >= 16 else 'FAIL'} |",
            f"| `Custom script instances` | 6 | **{custom_script_count}** | {'PASS' if custom_script_count >= 6 else 'FAIL'} |",
            f"| `player` GameObject | Present | **{'YES' if has_player else 'NO'}** | {'PASS' if has_player else 'FAIL'} |",
            f"| `Main Camera` GameObject | Present | **{'YES' if has_camera else 'NO'}** | {'PASS' if has_camera else 'FAIL'} |",
            f"| `GameManager` GameObject | Present | **{'YES' if has_gamemanager else 'NO'}** | {'PASS' if has_gamemanager else 'FAIL'} |",
            f"| `PlayerMovement` script instance | Present | **{'YES' if has_player_movement else 'NO'}** | {'PASS' if has_player_movement else 'FAIL'} |",
            "",
            f"**Custom Scripts Found:** `{', '.join(sorted(custom_scripts_found))}`",
            "",
        ]

        out_path = self.reports_dir / "pre_generation_verification.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(report_lines), encoding="utf-8")
        logger.info(f"Wrote Pre-Generation Verification report to {out_path}")

        # Assert mandatory critical requirements
        failures = []
        if not has_player:
            failures.append("Mandatory GameObject 'player' is missing from dataset.")
        if not has_camera:
            failures.append("Mandatory GameObject 'Main Camera' is missing from dataset.")
        if not has_gamemanager:
            failures.append("Mandatory GameObject 'GameManager' is missing from dataset.")
        if not has_player_movement:
            failures.append("Mandatory script instance 'PlayerMovement' is missing from dataset.")

        if failures:
            error_msg = f"Pre-Generation Verification FAILED with {len(failures)} critical errors: " + " | ".join(failures)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Pre-Generation Verification PASSED all mandatory checks!")
        return True
