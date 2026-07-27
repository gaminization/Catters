# Reconstruction Confidence Score Report

## Overall Reconstruction Confidence: **44.12%**

## Category Breakdown
| Category | Score | Status |
|---|---|---|
| Hierarchy | **13.37%** | WARN |
| Transforms | **13.37%** | WARN |
| Components | **100.0%** | PASS |
| Materials | **78.95%** | WARN |
| Meshes | **0.0%** | WARN |
| Scripts | **100.0%** | PASS |
| Serialized Fields | **0.0%** | WARN |
| Serialized References | **46.67%** | WARN |
| Assets | **44.7%** | WARN |

## Score Discrepancy Explanations
- Transforms (13.4%): Some transform position/scale deltas exceed 1e-5 tolerance.
- Assets (44.7%): Some dumped assets could not be matched by GUID to ExportedProject.
- Serialized References (46.7%): 32 PPtr pointers in MonoBehaviours refer to missing PathIDs.