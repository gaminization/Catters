"""Asset Matcher module matching dumped Unity assets to ExportedProject assets & GUIDs."""
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class ExportedAssetInfo:
    guid: str
    relative_path: str
    name: str
    extension: str


class AssetMatcher:
    """Matches dumped objects with ExportedProject asset files and GUIDs."""

    def __init__(self, exported_project_assets_dir: Path | str):
        self.assets_dir = Path(exported_project_assets_dir)
        self.asset_db_by_guid: dict[str, ExportedAssetInfo] = {}
        self.asset_db_by_name: dict[str, list[ExportedAssetInfo]] = {}

    def scan_exported_assets(self) -> None:
        """Traverses ExportedProject/Assets/ and index all .meta files."""
        if not self.assets_dir.exists():
            logger.warning(f"Assets directory not found: {self.assets_dir}")
            return

        for meta_file in self.assets_dir.glob("**/*.meta"):
            asset_file = meta_file.with_name(meta_file.stem)  # strip .meta
            guid = self._extract_guid(meta_file)
            if not guid:
                continue

            try:
                rel_path = asset_file.relative_to(self.assets_dir.parent).as_posix()
            except ValueError:
                rel_path = asset_file.as_posix()

            name = asset_file.stem
            ext = asset_file.suffix

            info = ExportedAssetInfo(
                guid=guid,
                relative_path=rel_path,
                name=name,
                extension=ext,
            )

            self.asset_db_by_guid[guid] = info
            norm_name = name.lower()
            if norm_name not in self.asset_db_by_name:
                self.asset_db_by_name[norm_name] = []
            self.asset_db_by_name[norm_name].append(info)

    def match_registry_assets(self, registry: PathIDRegistry) -> dict[Any, dict[str, Any]]:
        """Matches dumped registry objects (Mesh, Material, MonoScript, Avatar, etc.) to exported asset paths."""
        mapping: dict[Any, dict[str, Any]] = {}

        for obj in registry.all_objects:
            if obj.type_name in (
                "Mesh",
                "Material",
                "Texture2D",
                "Sprite",
                "Font",
                "Shader",
                "AnimatorController",
                "Avatar",
                "MonoScript",
                "Cubemap",
            ) or obj.class_id in (43, 21, 28, 213, 128, 48, 91, 90, 115, 89):

                matched_info = self._find_best_match(obj)
                info_dict = {
                    "path_id": obj.path_id,
                    "asset_file": obj.asset_file,
                    "type_name": obj.type_name,
                    "name": obj.name,
                    "matched": matched_info is not None,
                    "relative_path": matched_info.relative_path if matched_info else "",
                    "guid": matched_info.guid if matched_info else "",
                }
                mapping[obj.path_id] = info_dict
                mapping[str(obj.key)] = info_dict
                mapping[(obj.asset_file, obj.path_id)] = info_dict

        return mapping

    def _find_best_match(self, obj: UnityObject) -> Optional[ExportedAssetInfo]:
        norm_name = obj.name.lower()
        if norm_name in self.asset_db_by_name:
            candidates = self.asset_db_by_name[norm_name]
            type_ext_map = {
                "Material": ".mat",
                "MonoScript": ".cs",
                "Shader": ".shader",
                "AnimatorController": ".controller",
                "Avatar": ".asset",
                "Texture2D": ".png",
                "Mesh": [".asset", ".fbx", ".obj"],
            }
            preferred_exts = type_ext_map.get(obj.type_name, [])
            if isinstance(preferred_exts, str):
                preferred_exts = [preferred_exts]

            for cand in candidates:
                if preferred_exts and cand.extension.lower() in preferred_exts:
                    return cand
            return candidates[0]
        return None

    @staticmethod
    def _extract_guid(meta_file: Path) -> str:
        try:
            for line in meta_file.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("guid:"):
                    return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return ""
