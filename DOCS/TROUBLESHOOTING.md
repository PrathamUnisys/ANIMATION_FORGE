# Troubleshooting Guide

- **`RuleConflictError` on Task Execution**: Check if the task payload includes `auto_approve=True` or `overwrite_approved_asset=True`, which violate Tier 2 Constitutional rules.
- **`ToolchainNotApprovedError`**: Complete the R&D Lab review and click **Approve & Lock Toolchain** before running Character, Audio, or Animation departments.
- **`AnimaticGateBlockedError`**: Approve the Previs Animatic in Review Studio before launching full Animation rendering.
