"""Specialized parsers and property extractors for specific Unity types."""
from dataclasses import dataclass, field
from typing import Any, Optional

from recoverytool.parser.base import PPtr, UnityObject


@dataclass
class Vector3Data:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Vector3Data":
        if not isinstance(data, dict):
            return cls()
        return cls(
            x=float(data.get("X", data.get("x", 0.0))),
            y=float(data.get("Y", data.get("y", 0.0))),
            z=float(data.get("Z", data.get("z", 0.0))),
        )


@dataclass
class Vector4Data:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Vector4Data":
        if not isinstance(data, dict):
            return cls()
        return cls(
            x=float(data.get("X", data.get("x", 0.0))),
            y=float(data.get("Y", data.get("y", 0.0))),
            z=float(data.get("Z", data.get("z", 0.0))),
            w=float(data.get("W", data.get("w", 1.0))),
        )


class UnityObjectParsers:
    """Helper methods to extract structured properties from UnityObject dictionaries."""

    @staticmethod
    def parse_game_object(obj: UnityObject) -> dict[str, Any]:
        props = obj.properties
        components: list[PPtr] = []
        for comp_data in props.get("m_Components", []):
            components.append(PPtr.from_dict(comp_data))

        transform_pptr = PPtr()
        if "m_Transform" in props and isinstance(props["m_Transform"], dict):
            t_data = props["m_Transform"]
            transform_pptr = PPtr(
                file_id=int(t_data.get("m_FileID", 0)),
                path_id=int(t_data.get("m_PathID", 0)),
                name=str(t_data.get("type", "Transform")),
                is_null=False,
            )

        return {
            "name": str(props.get("m_Name", obj.name)),
            "active": bool(props.get("m_IsActive", True)),
            "layer": int(props.get("m_Layer", 0)),
            "tag": str(props.get("m_Tag", "Untagged")),
            "components": components,
            "transform_pptr": transform_pptr,
        }

    @staticmethod
    def parse_transform(obj: UnityObject) -> dict[str, Any]:
        props = obj.properties
        pos = Vector3Data.from_dict(props.get("m_LocalPosition"))
        rot = Vector4Data.from_dict(props.get("m_LocalRotation"))
        scale = Vector3Data.from_dict(props.get("m_LocalScale"))

        father = PPtr.from_dict(props.get("m_Father"))
        game_object = PPtr.from_dict(props.get("m_GameObject"))

        children: list[PPtr] = []
        for child_data in props.get("m_Children", []):
            children.append(PPtr.from_dict(child_data))

        res = {
            "position": pos,
            "rotation": rot,
            "scale": scale,
            "father": father,
            "game_object": game_object,
            "children": children,
            "is_rect_transform": obj.type_name == "RectTransform" or obj.class_id == 224,
        }

        if res["is_rect_transform"]:
            res["anchor_min"] = Vector3Data.from_dict(props.get("m_AnchorMin"))
            res["anchor_max"] = Vector3Data.from_dict(props.get("m_AnchorMax"))
            res["anchored_position"] = Vector3Data.from_dict(props.get("m_AnchoredPosition"))
            res["size_delta"] = Vector3Data.from_dict(props.get("m_SizeDelta"))
            res["pivot"] = Vector3Data.from_dict(props.get("m_Pivot"))

        return res

    @staticmethod
    def parse_mesh_filter(obj: UnityObject) -> dict[str, Any]:
        props = obj.properties
        mesh_pptr = PPtr.from_dict(props.get("m_Mesh"))
        game_object = PPtr.from_dict(props.get("m_GameObject"))
        return {"mesh": mesh_pptr, "game_object": game_object}

    @staticmethod
    def parse_mesh_renderer(obj: UnityObject) -> dict[str, Any]:
        props = obj.properties
        materials: list[PPtr] = []
        for mat_data in props.get("m_Materials", []):
            materials.append(PPtr.from_dict(mat_data))
        game_object = PPtr.from_dict(props.get("m_GameObject"))
        return {"materials": materials, "game_object": game_object}

    @staticmethod
    def parse_box_collider(obj: UnityObject) -> dict[str, Any]:
        props = obj.properties
        center = Vector3Data.from_dict(props.get("m_Center"))
        size = Vector3Data.from_dict(props.get("m_Size"))
        is_trigger = bool(props.get("m_IsTrigger", False))
        game_object = PPtr.from_dict(props.get("m_GameObject"))
        return {"center": center, "size": size, "is_trigger": is_trigger, "game_object": game_object}

    @staticmethod
    def parse_mono_behaviour(obj: UnityObject) -> dict[str, Any]:
        props = obj.properties
        script_pptr = PPtr.from_dict(props.get("m_Script"))
        game_object = PPtr.from_dict(props.get("m_GameObject"))
        enabled = bool(props.get("m_Enabled", True))

        # Extract non-standard serialized fields
        custom_fields: dict[str, Any] = {}
        standard_keys = {
            "m_GameObject",
            "m_Enabled",
            "m_Script",
            "m_Name",
            "type",
            "classID",
            "m_PathID",
            "byteSize",
        }
        for k, v in props.items():
            if k not in standard_keys:
                custom_fields[k] = v

        return {
            "script": script_pptr,
            "game_object": game_object,
            "enabled": enabled,
            "custom_fields": custom_fields,
        }
