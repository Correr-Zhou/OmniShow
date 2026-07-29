# Vendor: pose_custom

- Upstream: Local custom pose evaluator source from the video_gen_metrics workspace
- Commit: local source snapshot from 2026-07-28
- License: Project-specific custom code; bundled DWPose-related components may carry their own upstream licenses
- Local Path: vendor/pose_custom
- Copied At: 2026-07-28
- Copy Policy: Source required for AKD/PCK pose evaluation only. Weights, caches, generated outputs, unrelated annotators, and local runtime artifacts are excluded.
- Notes: This snapshot keeps the pose evaluator, metric utilities, and DWPose ONNX wrapper required by this evaluation pipeline.
