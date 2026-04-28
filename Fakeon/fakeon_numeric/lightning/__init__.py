"""fakeon_numeric.lightning — opt-in PyTorch Lightning helpers.

This subpackage is **not** imported by `fakeon_numeric` at top level.
It is opt-in because its contents depend on `torch` and
`pytorch_lightning`, neither of which is required by the rest of the
verification stack.  Importing this module will fail with the standard
`ModuleNotFoundError` if those libraries are not on the path; that is
intentional — keep the core suite torch-free, and let downstream users
who run real training opt in by installing the deps.
"""

from __future__ import annotations
