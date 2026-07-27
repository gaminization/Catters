"""CLI orchestrator executing Phase 11 & Final Phase Ground-Trip Scene Recovery Pipeline."""
import argparse
import sys
from pathlib import Path

from recoverytool.auditors.asset_auditor import AssetAuditor
from recoverytool.auditors.component_auditor import ComponentAuditor
from recoverytool.auditors.monobehaviour_auditor import MonoBehaviourAuditor
from recoverytool.auditors.transform_auditor import TransformAuditor
from recoverytool.confidence_engine import ConfidenceEngine
from recoverytool.database_builder import DatabaseBuilder
from recoverytool.editor.inspector_recovery import InspectorRecoveryEngine
from recoverytool.editor.validation import SceneValidator
from recoverytool.generator.csharp_tools_generator import CSharpToolsGenerator
from recoverytool.generator.editor_script_generator import EditorScriptGenerator
from recoverytool.generator.scene_reconstruction import SceneReconstructionEngine
from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.logger import PhaseLogger
from recoverytool.parser.dump_reader import DumpReader
from recoverytool.reports_generator import ReportGenerator
from recoverytool.resolver.asset_matcher import AssetMatcher
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver
from recoverytool.roundtrip.explainability_engine import ExplainabilityEngine
from recoverytool.roundtrip.loss_classifier import LossClassifier
from recoverytool.roundtrip.roundtrip_comparator import RoundtripComparator
from recoverytool.roundtrip.semantic_validator import SemanticValidator
from recoverytool.scene_diff import SceneDiffEngine
from recoverytool.visualizers.graph_visualizer import GraphVisualizer


def main() -> int:
    parser = argparse.ArgumentParser(description="Unity Scene Recovery & Roundtrip Pipeline")
    parser.add_argument(
        "--dump-dir",
        type=Path,
        default=Path("cattersrecovered/assetstudio/assetdump"),
        help="Path to AssetStudio assetdump directory",
    )
    parser.add_argument(
        "--exported-assets-dir",
        type=Path,
        default=Path("cattersrecovered/assetripper/ExportedProject/Assets"),
        help="Path to AssetRipper ExportedProject/Assets directory",
    )
    parser.add_argument(
        "--output-cs-dir",
        type=Path,
        default=Path("recoverytool/generated"),
        help="Path to output directory for generated C# editor scripts",
    )
    parser.add_argument(
        "--db-dir",
        type=Path,
        default=Path("recoverytool/database"),
        help="Path to database directory",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("recoverytool/reports"),
        help="Path to reports directory",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=Path("recoverytool/logs"),
        help="Path to logs directory",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Dry-run audit mode: Parse, resolve, validate, and generate reports without generating C# Unity code.",
    )

    args = parser.parse_args()

    phase_logger_mgr = PhaseLogger(args.logs_dir)
    logger = phase_logger_mgr.get_phase_logger("final_phase")

    logger.info("=== Starting Final Phase Unity Scene Recovery & Round-Trip Validation Pipeline ===")

    # 1. Read dumps & register objects (prefer direct APK bundle data.unity3d)
    registry = PathIDRegistry()
    apk_data = Path("extracted_apk/assets/bin/Data/data.unity3d")
    if apk_data.exists():
        from recoverytool.parser.apk_bundle_extractor import APKBundleExtractor
        extractor = APKBundleExtractor(apk_data)
        raw_objects = extractor.extract_and_register_all(registry)
    else:
        reader = DumpReader(args.dump_dir)
        raw_objects = reader.read_all()
        for obj in raw_objects:
            registry.register(obj)


    # 2. Resolve PPtr references
    resolver = ReferenceResolver(registry)
    resolver.resolve_all()

    # 3. Construct MultiDiGraph SceneGraph
    scene_graph = SceneGraph()
    scene_graph.build_from_registry(registry)
    recon_engine = SceneReconstructionEngine(scene_graph)
    reconstructed_roots = recon_engine.build_reconstructed_tree()

    # 4. Asset Matcher & Inspector Engine
    asset_matcher = AssetMatcher(args.exported_assets_dir)
    asset_matcher.scan_exported_assets()
    asset_mapping = asset_matcher.match_registry_assets(registry)

    scripts_dir = args.exported_assets_dir / "Scripts" / "Assembly-CSharp"
    inspector_engine = InspectorRecoveryEngine(scripts_dir)
    inspector_engine.scan_cs_scripts()
    inspector_engine.build_component_mapping(registry)


    # 5. Validation Engine
    validator = SceneValidator(registry)
    metrics = validator.validate(reconstructed_roots)
    metrics_dict = {
        "total_dumped_game_objects": metrics.total_dumped_game_objects,
        "reconstructed_game_objects": metrics.reconstructed_game_objects,
        "total_dumped_transforms": metrics.total_dumped_transforms,
        "reconstructed_transforms": metrics.reconstructed_transforms,
        "total_dumped_components": metrics.total_dumped_components,
        "reconstructed_components": metrics.reconstructed_components,
        "completeness_score_percent": metrics.completeness_score_percent,
    }

    # 6. Build Canonical Databases
    db_builder = DatabaseBuilder(args.db_dir)
    db_paths = db_builder.build_all(
        registry=registry,
        resolver=resolver,
        scene_graph=scene_graph,
        asset_mapping=asset_mapping,
        reconstructed_roots=reconstructed_roots,
        validation_metrics_dict=metrics_dict,
    )
    logger.info(f"Canonical database files written to {args.db_dir}")

    # 7. Audits & Diff Engines
    diff_engine = SceneDiffEngine(registry, db_paths["scene"])
    diff_engine.compute_diff()
    diff_engine.generate_report(args.reports_dir / "scene_diff.md")

    t_auditor = TransformAuditor(registry, db_paths["scene"])
    t_items = t_auditor.audit()
    t_auditor.generate_report(args.reports_dir / "transform_validation.md")

    c_auditor = ComponentAuditor(registry, db_paths["scene"])
    c_items = c_auditor.audit()
    c_auditor.generate_report(args.reports_dir / "component_validation.md")

    a_auditor = AssetAuditor(registry, asset_mapping)
    a_items = a_auditor.audit()
    a_auditor.generate_report(args.reports_dir / "asset_validation.md")

    mb_auditor = MonoBehaviourAuditor(registry, inspector_engine)
    mb_items = mb_auditor.audit()
    mb_auditor.generate_report(args.reports_dir / "monobehaviour_validation.md")

    # Deep Inventory Inspector (Phases 1-5 Diagnostic Report)
    from recoverytool.auditors.deep_inventory_inspector import DeepInventoryInspector
    deep_inspector = DeepInventoryInspector(registry, asset_mapping, inspector_engine, args.db_dir, args.reports_dir)
    deep_inspector.run_full_diagnostic()



    # 8. Round-Trip Validation Engines
    exported_json_path = args.db_dir / "scene_export.json"
    roundtrip_comp = RoundtripComparator(db_paths["scene"], exported_json_path)
    roundtrip_diffs = roundtrip_comp.compare()
    roundtrip_comp.generate_report(args.reports_dir / "roundtrip_diff.md")

    sem_val = SemanticValidator(registry, db_paths["scene"])
    sem_metrics = sem_val.validate_equivalence()

    loss_clf = LossClassifier(registry, asset_mapping)
    loss_summaries = loss_clf.classify()
    loss_clf.generate_report(args.reports_dir / "information_loss.md")

    exp_engine = ExplainabilityEngine(registry, asset_mapping)
    exp_engine.generate_report(args.reports_dir / "explainability_report.md")

    # 9. Visual HTML Graphs
    visualizer = GraphVisualizer(scene_graph)
    visualizer.generate_dependency_graph_html(args.reports_dir / "dependency_graph.html")
    visualizer.generate_scene_graph_html(args.reports_dir / "scene_graph.html")

    # 10. Confidence & Reports
    conf_engine = ConfidenceEngine()
    scores = conf_engine.calculate_confidence(t_items, c_items, a_items, mb_items)
    conf_engine.generate_report(scores, args.reports_dir / "confidence_breakdown.md")

    report_gen = ReportGenerator(args.reports_dir)
    report_gen.generate_object_statistics(registry, len(raw_objects))
    report_gen.generate_scene_hierarchy(reconstructed_roots)
    report_gen.generate_object_counts(registry)
    report_gen.generate_broken_references(resolver)
    report_gen.generate_asset_mapping_report(asset_mapping)
    report_gen.generate_statistics(registry, resolver)
    report_gen.generate_final_audit_report(scores.overall, scores.explanations)
    report_gen.generate_ground_truth_report(
        overall_score=scores.overall,
        semantic_score=sem_metrics.equivalence_score_percent,
        roundtrip_diff_count=len(roundtrip_diffs),
        loss_summaries=loss_summaries,
    )
    validator.generate_validation_report(metrics, args.reports_dir / "validation_report.md")

    # 11. C# Unity Tools Generation (RecoverScene.cs, ExportScene.cs, ValidateScene.cs)
    # 6. Pre-Generation Dataset Verification
    from recoverytool.auditors.pre_generation_verifier import PreGenerationVerifier
    verifier = PreGenerationVerifier(registry, args.reports_dir)
    verifier.verify_and_report()

    if not args.audit:
        output_cs_file = args.output_cs_dir / "RecoverScene.cs"
        script_gen = EditorScriptGenerator(asset_mapping, inspector_engine, output_cs_file)
        script_gen.generate_from_scene_json(db_paths["scene"])

        cs_tools_gen = CSharpToolsGenerator(args.output_cs_dir)
        cs_tools_gen.generate_export_scene_script()
        cs_tools_gen.generate_validate_scene_script()

        # Copy to ExportedProject Editor directory if present
        exported_editor_dir = args.exported_assets_dir / "Editor"
        if exported_editor_dir.exists():
            editor_recover_file = exported_editor_dir / "RecoverScene.cs"
            script_gen_exported = EditorScriptGenerator(asset_mapping, inspector_engine, editor_recover_file)
            script_gen_exported.generate_from_scene_json(db_paths["scene"])

            cs_tools_gen_exported = CSharpToolsGenerator(exported_editor_dir)
            cs_tools_gen_exported.generate_export_scene_script()
            cs_tools_gen_exported.generate_validate_scene_script()
            logger.info(f"Updated C# Unity Editor tools in ExportedProject at {exported_editor_dir}")

        logger.info(f"Generated C# Unity Editor tools (RecoverScene.cs, ExportScene.cs, ValidateScene.cs) at {args.output_cs_dir}")
    else:
        logger.info("--audit dry-run mode active: Skipped C# code generation.")


    logger.info("=== Ground Truth Round-Trip Validation Pipeline Completed Successfully! ===")
    logger.info(f"Overall Reconstruction Confidence: {scores.overall}%")
    logger.info(f"Semantic Equivalence Score: {sem_metrics.equivalence_score_percent}%")
    logger.info(f"Round-Trip Discrepancies Count: {len(roundtrip_diffs)}")
    logger.info(f"Deliverables exported to {args.reports_dir} and {args.db_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
