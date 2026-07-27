"""PathID Registry module tracking and resolving Unity objects by AssetKey (file_name, path_id) and PathID."""
import logging
from typing import Optional, Union

from recoverytool.parser.base import AssetKey, UnityObject

logger = logging.getLogger(__name__)


class PathIDRegistry:
    """Registry mapping composite AssetKeys and PathIDs to UnityObject instances."""

    def __init__(self):
        self._by_key: dict[AssetKey, UnityObject] = {}
        self._by_path_id: dict[int, UnityObject] = {}
        self._duplicates: dict[int, list[UnityObject]] = {}

    def register(self, obj: UnityObject) -> None:
        if obj.path_id == 0:
            return

        key = obj.key
        self._by_key[key] = obj

        if obj.path_id in self._by_path_id:
            existing = self._by_path_id[obj.path_id]
            if obj.path_id not in self._duplicates:
                self._duplicates[obj.path_id] = [existing]
            self._duplicates[obj.path_id].append(obj)

            # Prefer level0 / sharedassets0 / richer objects in path_id index
            priority_files = {"level0", "sharedassets0.assets", "resources.assets"}
            if obj.asset_file in priority_files and existing.asset_file not in priority_files:
                self._by_path_id[obj.path_id] = obj
            elif existing.type_name == "Unknown" and obj.type_name != "Unknown":
                self._by_path_id[obj.path_id] = obj
        else:
            self._by_path_id[obj.path_id] = obj

    def get_by_key(self, file_name: str, path_id: int) -> Optional[UnityObject]:
        """Looks up object by composite (file_name, path_id) key."""
        return self._by_key.get(AssetKey(file_name, path_id))

    def get(self, key_or_path_id: Union[int, AssetKey, tuple[str, int]]) -> Optional[UnityObject]:
        """Looks up object by PathID, AssetKey, or tuple."""
        if isinstance(key_or_path_id, AssetKey):
            return self._by_key.get(key_or_path_id)
        elif isinstance(key_or_path_id, tuple) and len(key_or_path_id) == 2:
            return self._by_key.get(AssetKey(key_or_path_id[0], key_or_path_id[1]))
        elif isinstance(key_or_path_id, int):
            return self._by_path_id.get(key_or_path_id)
        return None

    def contains(self, key_or_path_id: Union[int, AssetKey, tuple[str, int]]) -> bool:
        if isinstance(key_or_path_id, AssetKey):
            return key_or_path_id in self._by_key
        elif isinstance(key_or_path_id, tuple) and len(key_or_path_id) == 2:
            return AssetKey(key_or_path_id[0], key_or_path_id[1]) in self._by_key
        elif isinstance(key_or_path_id, int):
            return key_or_path_id in self._by_path_id
        return False

    @property
    def all_objects(self) -> list[UnityObject]:
        return list(self._by_key.values())

    @property
    def duplicate_count(self) -> int:
        return len(self._duplicates)

    def get_duplicates(self) -> dict[int, list[UnityObject]]:
        return self._duplicates
