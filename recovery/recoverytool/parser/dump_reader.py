"""AssetStudio Dump Reader module."""
import json
import logging
from pathlib import Path
from typing import Any, Generator, Optional

from recoverytool.parser.base import PPtr, UnityObject

logger = logging.getLogger(__name__)


def extract_pptrs_from_data(data: Any) -> list[PPtr]:
    """Recursively extracts all PPtr reference objects from nested dictionary/list data."""
    pptrs: list[PPtr] = []
    if isinstance(data, dict):
        if "m_PathID" in data and ("m_FileID" in data or "IsNull" in data or "Name" in data):
            pptrs.append(PPtr.from_dict(data))
        for key, val in data.items():
            if key != "m_PathID":  # avoid self pathID
                pptrs.extend(extract_pptrs_from_data(val))
    elif isinstance(data, list):
        for item in data:
            pptrs.extend(extract_pptrs_from_data(item))
    return pptrs


class DumpReader:
    """Reads and parses JSON asset dumps from AssetStudio output directory."""

    def __init__(self, dump_dir: Path | str):
        self.dump_dir = Path(dump_dir)

    def iter_files(self) -> Generator[Path, None, None]:
        """Yields all .txt files in dump_dir."""
        if not self.dump_dir.exists():
            logger.warning(f"Dump directory does not exist: {self.dump_dir}")
            return
        for file_path in sorted(self.dump_dir.glob("*.txt")):
            yield file_path

    def parse_file(self, file_path: Path) -> Optional[UnityObject]:
        """Parses a single dumped JSON file into a UnityObject instance."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace").strip()
            if not content:
                return None
            data = json.loads(content)
            if not isinstance(data, dict):
                return None

            path_id = int(data.get("m_PathID", 0))
            class_id = int(data.get("classID", 0))
            type_name = str(data.get("type", "Unknown"))
            name = str(data.get("m_Name", data.get("Name", file_path.stem)))

            references = extract_pptrs_from_data(data)

            return UnityObject(
                path_id=path_id,
                class_id=class_id,
                type_name=type_name,
                name=name,
                properties=data,
                raw_data=data,
                references=references,
                file_path=str(file_path),
            )
        except Exception as err:
            logger.debug(f"Failed to parse dump file {file_path.name}: {err}")
            return None

    def read_all(self) -> list[UnityObject]:
        """Reads all dump files in dump_dir and returns parsed UnityObjects."""
        objects: list[UnityObject] = []
        for file_path in self.iter_files():
            obj = self.parse_file(file_path)
            if obj is not None:
                objects.append(obj)
        return objects
