"""Inspector Recovery module extracting MonoBehaviour serialized fields and values."""
import logging
import re
from pathlib import Path
from typing import Any, Optional

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


class InspectorRecoveryEngine:
    """Extracts C# script serialized field definitions and formats C# assignments."""

    def __init__(self, scripts_dir: Path | str):
        self.scripts_dir = Path(scripts_dir)
        self.script_field_types: dict[str, dict[str, str]] = {}  # ScriptName -> {FieldName: TypeStr}
        self.comp_to_go: dict[int, int] = {}  # Component PathID -> Owning GameObject PathID

    def build_component_mapping(self, registry: PathIDRegistry) -> None:
        """Builds mapping from component PathIDs to owning GameObject PathIDs."""
        self.comp_to_go.clear()
        for obj in registry.all_objects:
            if obj.type_name != "GameObject":
                m_go = obj.properties.get("m_GameObject", {})
                if isinstance(m_go, dict):
                    go_pid = m_go.get("m_PathID", 0)
                    if go_pid:
                        self.comp_to_go[obj.path_id] = go_pid

    def scan_cs_scripts(self) -> None:
        """Parses C# script files to discover field names and types."""
        if not self.scripts_dir.exists():
            logger.warning(f"Scripts directory not found: {self.scripts_dir}")
            return

        for cs_file in self.scripts_dir.glob("**/*.cs"):
            script_name = cs_file.stem
            fields = self._parse_cs_fields(cs_file)
            self.script_field_types[script_name] = fields

    def format_field_assignment(
        self, comp_var_name: str, script_name: str, field_name: str, val: Any
    ) -> Optional[str]:
        """Formats a C# assignment statement for a component variable and field value."""
        if val is None:
            return None

        field_type = self.script_field_types.get(script_name, {}).get(field_name, "")
        cs_val = self._to_cs_literal(val, field_type)
        if cs_val is None:
            return None

        return f"            {comp_var_name}.{field_name} = {cs_val};"

    def _to_cs_literal(self, val: Any, field_type: str = "") -> Optional[str]:
        if isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, (int, float)):
            if isinstance(val, float):
                return f"{val}f"
            return str(val)
        elif isinstance(val, str):
            escaped = val.replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(val, dict):
            # Check if Vector3 dict
            if "X" in val or "x" in val:
                x = val.get("X", val.get("x", 0.0))
                y = val.get("Y", val.get("y", 0.0))
                z = val.get("Z", val.get("z", 0.0))
                return f"new Vector3({x}f, {y}f, {z}f)"
            # Check if PPtr dict
            if "m_PathID" in val:
                raw_pid = val["m_PathID"]
                if raw_pid == 0:
                    return "null"
                go_pid = self.comp_to_go.get(raw_pid, raw_pid)
                if field_type == "Transform":
                    return f"createdObjects.ContainsKey({go_pid}) ? createdObjects[{go_pid}].transform : null"
                elif field_type == "GameObject":
                    return f"createdObjects.ContainsKey({go_pid}) ? createdObjects[{go_pid}] : null"
                elif field_type:
                    return f"createdObjects.ContainsKey({go_pid}) ? createdObjects[{go_pid}].GetComponent<{field_type}>() : null"
                else:
                    return f"createdObjects.ContainsKey({go_pid}) ? createdObjects[{go_pid}] : null"
        return None

    @staticmethod
    def _parse_cs_fields(cs_file: Path) -> dict[str, str]:
        fields: dict[str, str] = {}
        try:
            code = cs_file.read_text(encoding="utf-8", errors="replace")
            pattern = re.compile(
                r"(?:public|\[SerializeField\]\s*(?:private|protected)?)\s+([\w<>]+)\s+(\w+)\s*;",
                re.MULTILINE,
            )
            for match in pattern.finditer(code):
                type_str, field_name = match.groups()
                fields[field_name] = type_str
        except Exception as err:
            logger.debug(f"Error parsing script {cs_file.name}: {err}")
        return fields
