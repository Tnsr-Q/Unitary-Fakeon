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

from .distributed_hessian_pl import DistributedHessianPLCallback
from .hessian_pl_callback import HessianPLCallback

from .checkpointed_hessian_pl import CheckpointedDistributedHessianPLCallback
from .zero3_hessian_pl import Zero3CheckpointedHessianPLCallback
from .zero3_compressed_hessian_pl import CompressedZero3HessianPLCallback
from .fp8_zero3_hessian_pl import FP8Zero3HessianPLCallback
from .zeroinfinity_fp8_hessian_pl import ZeroInfinityFP8HessianPLCallback
from .zeroinfinity_cpu_fallback_pl import CPUFallbackZeroInfinityCallback

__all__ = ["HessianPLCallback", "DistributedHessianPLCallback", "CheckpointedDistributedHessianPLCallback", "Zero3CheckpointedHessianPLCallback", "CompressedZero3HessianPLCallback", "FP8Zero3HessianPLCallback", "ZeroInfinityFP8HessianPLCallback", "CPUFallbackZeroInfinityCallback"]
