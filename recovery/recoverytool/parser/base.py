"""Base data classes representing serialized Unity objects, PPtr references, and composite keys."""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class AssetKey:
    """Composite unique identifier for a serialized Unity object within an APK bundle."""

    file_name: str
    path_id: int

    def __str__(self) -> str:
        return f"{self.file_name}#{self.path_id}"


@dataclass
class PPtr:
    """Represents a Pointer to a Persistent object (PPtr) in Unity serialized data."""

    file_id: int = 0
    path_id: int = 0
    name: str = ""

    @property
    def is_null(self) -> bool:
        return self.path_id == 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PPtr":
        if not isinstance(data, dict):
            return cls(0, 0, "")
        fid = data.get("m_FileID", data.get("fileID", 0))
        pid = data.get("m_PathID", data.get("pathID", 0))
        name = data.get("Name", data.get("name", ""))
        return cls(file_id=fid, path_id=pid, name=name)


@dataclass
class UnityObject:
    """Represents a single serialized Unity object extracted from binary files."""

    path_id: int
    class_id: int
    type_name: str
    name: str = ""
    asset_file: str = "level0"
    properties: dict[str, Any] = field(default_factory=dict)
    resolved_references: dict[str, Any] = field(default_factory=dict)
    raw_data: Any = None
    file_path: str = ""
    _custom_references: Optional[list[PPtr]] = None

    def __init__(
        self,
        path_id: int,
        class_id: int,
        type_name: str,
        name: str = "",
        asset_file: str = "level0",
        properties: Optional[dict[str, Any]] = None,
        resolved_references: Optional[dict[str, Any]] = None,
        raw_data: Any = None,
        file_path: str = "",
        references: Optional[list[PPtr]] = None,
    ):
        self.path_id = path_id
        self.class_id = class_id
        self.type_name = type_name
        self.name = name
        self.asset_file = asset_file
        self.properties = properties if properties is not None else {}
        self.resolved_references = resolved_references if resolved_references is not None else {}
        self.raw_data = raw_data
        self.file_path = file_path
        self._custom_references = references

    @property
    def key(self) -> AssetKey:
        return AssetKey(self.asset_file, self.path_id)

    @property
    def references(self) -> list[PPtr]:
        """Extracts PPtr references embedded in properties or returns custom references."""
        if self._custom_references is not None:
            return self._custom_references

        refs: list[PPtr] = []

        def _extract(data: Any) -> None:
            if isinstance(data, dict):
                if "m_PathID" in data or "pathID" in data:
                    refs.append(PPtr.from_dict(data))
                for v in data.values():
                    _extract(v)
            elif isinstance(data, list):
                for item in data:
                    _extract(item)

        _extract(self.properties)
        return refs
