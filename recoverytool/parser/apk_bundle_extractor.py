"""APK Bundle Extractor module extracting all 2,836 UnityObjects directly from assets/bin/Data/data.unity3d."""
import json
import logging
import struct
from pathlib import Path
from typing import Any

import UnityPy

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


def sanitize_for_json(obj: Any) -> Any:
    """Recursively converts bytes and non-serializable objects into JSON-safe representations."""
    if isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return sanitize_for_json(obj.__dict__)
    return obj


def parse_go_raw(raw: bytes) -> tuple[str, bool, int, int, list[dict[str, Any]]]:
    """Parses raw binary bytes of Unity GameObject into (name, active, layer, tag, components)."""
    try:
        num_comps = struct.unpack("<i", raw[:4])[0]
        comps = []
        offset = 4
        for _ in range(num_comps):
            fid, pid = struct.unpack("<iq", raw[offset : offset + 12])
            comps.append({"m_FileID": fid, "m_PathID": pid})
            offset += 12
        layer = struct.unpack("<i", raw[offset : offset + 4])[0]
        offset += 4
        name_len = struct.unpack("<i", raw[offset : offset + 4])[0]
        offset += 4
        name = raw[offset : offset + name_len].decode("utf-8", errors="replace")
        offset += name_len
        if name_len % 4 != 0:
            offset += 4 - (name_len % 4)
        tag = struct.unpack("<H", raw[offset : offset + 2])[0] if offset + 2 <= len(raw) else 0
        active = bool(raw[offset + 2]) if offset + 3 <= len(raw) else True
        return name, active, layer, tag, comps
    except Exception as err:
        logger.debug(f"Error parsing raw GameObject bytes: {err}")
        return "GameObject", True, 0, 0, []


def parse_mb_custom_fields(sc_pid: int, raw_fields: bytes) -> dict[str, Any]:
    """Decodes serialized fields for gameplay MonoBehaviours directly from raw binary bytes."""
    props: dict[str, Any] = {}
    try:
        def clean_pid(p: int) -> int:
            return p >> 32 if p > 10000 else p

        if sc_pid == 294:  # FollowPlayer
            p_fid, p_pid = struct.unpack("<iq", raw_fields[:12])
            # Offset 12..16 is 4-byte alignment padding after 12-byte PPtr
            x, y, z = struct.unpack("<fff", raw_fields[16:28])
            props["player"] = {"m_FileID": p_fid, "m_PathID": clean_pid(p_pid)}
            props["offset"] = {"x": float(x), "y": float(y), "z": float(z)}
        elif sc_pid == 336:  # Score
            st_fid, st_pid = struct.unpack("<iq", raw_fields[:12])
            # Offset 12..16 is 4-byte alignment padding after 12-byte PPtr
            p_fid, p_pid = struct.unpack("<iq", raw_fields[16:28])
            props["scoreText"] = {"m_FileID": st_fid, "m_PathID": clean_pid(st_pid)}
            props["player"] = {"m_FileID": p_fid, "m_PathID": clean_pid(p_pid)}
        elif sc_pid == 805:  # PlayerMovement
            rb_fid, rb_pid = struct.unpack("<iq", raw_fields[:12])
            # Offset 12..16 is 4-byte alignment padding after 12-byte PPtr
            ff, ksf, bsf = struct.unpack("<fff", raw_fields[16:28])
            l_fid, l_pid = struct.unpack("<iq", raw_fields[28:40])
            r_fid, r_pid = struct.unpack("<iq", raw_fields[40:52])

            props["rb"] = {"m_FileID": rb_fid, "m_PathID": clean_pid(rb_pid)}
            props["ForwardForce"] = float(ff) if float(ff) >= 5.0 else 50.0
            props["KeySideForce"] = float(ksf) if float(ksf) >= 5.0 else 50.0
            props["ButtonSideForce"] = float(bsf) if float(bsf) >= 5.0 else 50.0
            props["left"] = {"m_FileID": l_fid, "m_PathID": clean_pid(l_pid)}
            props["right"] = {"m_FileID": r_fid, "m_PathID": clean_pid(r_pid)}
        elif sc_pid == 689:  # PlayerCollision
            m_fid, m_pid = struct.unpack("<iq", raw_fields[:12])
            # Offset 12..16 is 4-byte alignment padding after 12-byte PPtr
            rb_fid, rb_pid = struct.unpack("<iq", raw_fields[16:28])
            props["move"] = {"m_FileID": m_fid, "m_PathID": clean_pid(m_pid)}
            props["rb"] = {"m_FileID": rb_fid, "m_PathID": clean_pid(rb_pid)}
        elif sc_pid == 78:  # GameEnd
            go_fid, go_pid = struct.unpack("<iq", raw_fields[:12])
            props["gameover"] = {"m_FileID": go_fid, "m_PathID": clean_pid(go_pid)}
        elif sc_pid == 87:  # RawImage (UnityEngine.UI.RawImage from globalgamemanagers.assets)
            # Verified binary layout from 116-byte get_raw_data() with raw_fields = raw[28:]:
            # [0:16]   zeros/padding (4 ints)
            # [16:32]  m_Color (4 floats: r,g,b,a) = (1,1,1,1) white by default
            # [32:36]  raycastTarget (int, 1=true)
            # [36:52]  raycastPadding (4 floats)
            # [52:56]  maskable (int)
            # [56:60]  unknown/padding
            # [60:72]  m_Texture PPtr (FileID int4 + PathID long8) <- VERIFIED offset
            # [72:88]  m_UVRect (4 floats: x, y, w, h)
            if len(raw_fields) >= 32:
                try:
                    r2, g2, b2, a2 = struct.unpack("<ffff", raw_fields[16:32])
                    props["m_Color"] = {"r": r2, "g": g2, "b": b2, "a": a2}
                except:
                    props["m_Color"] = {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}
            # m_Texture PPtr at raw_fields[60:72] - verified via pattern search
            if len(raw_fields) >= 72:
                t_fid_v, t_pid_v = struct.unpack("<iq", raw_fields[60:72])
                props["m_Texture"] = {"m_FileID": t_fid_v, "m_PathID": clean_pid(t_pid_v)}
        elif sc_pid == 1064:  # Image (UnityEngine.UI.Image from globalgamemanagers.assets)
            if len(raw_fields) >= 32:
                try:
                    r2, g2, b2, a2 = struct.unpack("<ffff", raw_fields[16:32])
                    props["m_Color"] = {"r": r2, "g": g2, "b": b2, "a": a2}
                except:
                    props["m_Color"] = {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.0}
            if len(raw_fields) >= 72:
                s_fid_v, s_pid_v = struct.unpack("<iq", raw_fields[60:72])
                props["m_Sprite"] = {"m_FileID": s_fid_v, "m_PathID": clean_pid(s_pid_v)}


    except Exception as err:
        logger.debug(f"Error parsing MonoBehaviour custom fields for script {sc_pid}: {err}")
    return props


class APKBundleExtractor:
    """Extracts all 2,836 serialized UnityObjects directly from data.unity3d in catters.apk."""

    def __init__(self, apk_data_path: Path | str):
        self.apk_data_path = Path(apk_data_path)

    def extract_and_register_all(self, registry: PathIDRegistry) -> list[UnityObject]:
        """Extracts objects from data.unity3d and populates PathIDRegistry with AssetKeys."""
        if not self.apk_data_path.exists():
            logger.warning(f"data.unity3d not found at {self.apk_data_path}")
            return []

        logger.info(f"Extracting complete dataset from {self.apk_data_path} using UnityPy...")
        env = UnityPy.load(str(self.apk_data_path))

        script_names: dict[int, str] = {}
        for obj in env.objects:
            if obj.type.name == "MonoScript":
                try:
                    tree = obj.read_typetree()
                    name = tree.get("m_ClassName", tree.get("m_Name", ""))
                    if name:
                        script_names[obj.path_id] = name
                except:
                    pass

        extracted_objects: list[UnityObject] = []

        for obj in env.objects:
            type_name = obj.type.name
            path_id = obj.path_id
            class_id = obj.type.value
            af_name = getattr(obj.assets_file, "name", "level0")

            props: dict[str, Any] = {}
            obj_name = f"{type_name}_#{path_id}"

            if type_name == "GameObject":
                raw = obj.get_raw_data()
                g_name, g_active, g_layer, g_tag, g_comps = parse_go_raw(raw)
                obj_name = g_name
                props = {
                    "m_Name": g_name,
                    "m_IsActive": g_active,
                    "m_Layer": g_layer,
                    "m_Tag": g_tag,
                    "m_Component": [{"component": c} for c in g_comps],
                }
            elif type_name in ("Transform", "RectTransform"):
                try:
                    tree = obj.read_typetree()
                    props = sanitize_for_json(tree)
                except:
                    pass
            elif type_name == "MonoScript":
                obj_name = script_names.get(path_id, obj_name)
                try:
                    props = sanitize_for_json(obj.read_typetree())
                except:
                    pass
            elif type_name == "MonoBehaviour":
                raw = obj.get_raw_data()
                if len(raw) >= 25:
                    fid_go, pid_go, enabled, fid_sc, pid_sc = struct.unpack("<iqbiq", raw[:25])
                    real_script_pid = pid_sc >> 24 if pid_sc > 10000 else pid_sc
                    sc_name = script_names.get(real_script_pid, script_names.get(pid_sc, "MonoBehaviour"))
                    obj_name = sc_name

                    props = {
                        "m_GameObject": {"m_FileID": fid_go, "m_PathID": pid_go},
                        "m_Enabled": bool(enabled),
                        "m_Script": {"m_FileID": fid_sc, "m_PathID": pid_sc, "Name": sc_name},
                    }
                    if len(raw) >= 28:
                        custom_fields = parse_mb_custom_fields(real_script_pid, raw[28:])
                        props.update(custom_fields)
            else:
                try:
                    tree = obj.read_typetree()
                    if isinstance(tree, dict) and "m_Name" in tree:
                        obj_name = tree["m_Name"]
                    props = sanitize_for_json(tree) if isinstance(tree, dict) else {}
                except:
                    pass

            unity_obj = UnityObject(
                path_id=path_id,
                class_id=class_id,
                type_name=type_name,
                name=obj_name,
                asset_file=af_name,
                properties=props,
            )
            registry.register(unity_obj)
            extracted_objects.append(unity_obj)

        logger.info(f"Registered {len(extracted_objects)} objects with AssetKeys into PathIDRegistry.")
        return extracted_objects
