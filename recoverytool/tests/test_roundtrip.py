"""Unit tests for Final Phase round-trip validation modules."""
from pathlib import Path
import pytest

from recoverytool.generator.csharp_tools_generator import CSharpToolsGenerator
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.roundtrip.explainability_engine import ExplainabilityEngine
from recoverytool.roundtrip.loss_classifier import LossClassifier
from recoverytool.roundtrip.roundtrip_comparator import RoundtripComparator
from recoverytool.roundtrip.semantic_validator import SemanticValidator


def test_csharp_tools_generator(tmp_path):
    gen = CSharpToolsGenerator(tmp_path)
    export_cs = gen.generate_export_scene_script()
    validate_cs = gen.generate_validate_scene_script()

    assert export_cs.exists()
    assert validate_cs.exists()
    assert "public static class ExportScene" in export_cs.read_text(encoding="utf-8")
    assert "public static class ValidateScene" in validate_cs.read_text(encoding="utf-8")


def test_roundtrip_comparator(tmp_path):
    canon_file = tmp_path / "scene.json"
    canon_file.write_text('{"root_objects": [{"name": "Canvas", "path_id": 40, "tag": "Untagged", "layer": 0}]}', encoding="utf-8")

    exported_file = tmp_path / "scene_export.json"
    exported_file.write_text('{"root_objects": [{"name": "Canvas", "path_id": 40, "tag": "Untagged", "layer": 0}]}', encoding="utf-8")

    comparator = RoundtripComparator(canon_file, exported_file)
    diffs = comparator.compare()
    assert len(diffs) == 0

    report_path = tmp_path / "roundtrip_diff.md"
    comparator.generate_report(report_path)
    assert report_path.exists()


def test_loss_classifier_and_explainability():
    registry = PathIDRegistry()
    go_obj = UnityObject(path_id=40, class_id=1, type_name="GameObject", name="Canvas")
    registry.register(go_obj)

    classifier = LossClassifier(registry, {})
    summaries = classifier.classify()
    assert len(summaries) == 5

    exp_engine = ExplainabilityEngine(registry, {})
    items = exp_engine.evaluate_explainability()
    assert len(items) == 1
    assert items[0].source == "Raw Dump"
