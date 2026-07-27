"""Unit tests for recoverytool.parser modules."""
from pathlib import Path
import pytest

from recoverytool.parser.base import PPtr, UnityObject
from recoverytool.parser.dump_reader import DumpReader
from recoverytool.parser.object_parsers import UnityObjectParsers, Vector3Data, Vector4Data


def test_pptr_creation():
    pptr = PPtr.from_dict({"m_FileID": 0, "m_PathID": 40, "Name": "Canvas", "IsNull": False})
    assert pptr.file_id == 0
    assert pptr.path_id == 40
    assert pptr.name == "Canvas"
    assert not pptr.is_null


def test_dump_reader_canvas(tmp_path):
    canvas_json = """{
        "m_Components": [{"Name": "RectTransform", "IsNull": false, "m_FileID": 0, "m_PathID": 1572}],
        "m_Name": "Canvas",
        "m_PathID": 40,
        "type": "GameObject",
        "classID": 1
    }"""
    dump_file = tmp_path / "Canvas.txt"
    dump_file.write_text(canvas_json, encoding="utf-8")

    reader = DumpReader(tmp_path)
    objects = reader.read_all()
    assert len(objects) == 1
    obj = objects[0]
    assert obj.path_id == 40
    assert obj.type_name == "GameObject"
    assert obj.class_id == 1
    assert obj.name == "Canvas"

    go_info = UnityObjectParsers.parse_game_object(obj)
    assert len(go_info["components"]) == 1
    assert go_info["components"][0].path_id == 1572
