"""
tests/test_unitarity_closure.py

Numerical counterpart of `Fakeon/QFT/FakeonUnitarity.lean::perturbative_unitarity_closure`.

We construct synthetic inputs that simultaneously satisfy the three
hypotheses of the theorem, on the *canonical* basis where the projector
is the simplest:

    P_phys = diag(1, …, 1, 0, …, 0).       (k physical, n-k fakeon)

The Hermitian generator is built block-diagonal,

    H = block_diag(H_phys, H_fak),

with `H_phys` a generic k×k Hermitian matrix and `H_fak` a real
symmetric (n-k)×(n-k) matrix.  Then

    T = H                       (Hermitian),
    S = exp(i H)                (exactly unitary).

Consequences:
  (1)  P_phys · S† · S · P_phys = P_phys             — exact,
  (2)  Eigenvalues of P_phys · S · P_phys live on the unit circle ∪ {0},
  (3)  Q · T · Q = block_diag(0, H_fak) is real      — entrywise.

If any of these fail at machine precision, the corresponding hypothesis
in `Fakeon/QFT/FakeonUnitarity.lean` is being violated by our model
construction, not by the theorem.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.linalg import expm


# ---------------------------------------------------------------------------
# Synthetic inputs (canonical basis, block-diagonal generator).
# ---------------------------------------------------------------------------

def _build_inputs(
    n: int = 6, k: int = 4, seed: int = 17, scale: float = 0.3
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (P_phys, T, S) on the canonical basis.

    H = block_diag(H_phys, H_fak):
      H_phys ∈ ℂ^{k×k} Hermitian,
      H_fak  ∈ ℝ^{(n-k)×(n-k)} real symmetric.
    T = H, S = exp(iH).
    """
    rng = np.random.default_rng(seed)

    # P_phys = diag(1,…,1,0,…,0).
    P = np.diag([1.0] * k + [0.0] * (n - k)).astype(complex)

    # H_phys: Hermitian.
    A = rng.standard_normal((k, k)) + 1j * rng.standard_normal((k, k))
    H_phys = scale * 0.5 * (A + A.conj().T)

    # H_fak: real symmetric (Hermitian and real entries).
    B = rng.standard_normal((n - k, n - k))
    H_fak = scale * 0.5 * (B + B.T)

    # Block-diagonal embedding into n×n.
    H = np.zeros((n, n), dtype=complex)
    H[:k, :k] = H_phys
    H[k:, k:] = H_fak.astype(complex)

    T = H                      # already Hermitian
    S = expm(1j * H)           # exactly unitary
    return P, T, S


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------

def test_p_phys_is_orthogonal_projector() -> None:
    P, _, _ = _build_inputs()
    assert np.allclose(P @ P, P, atol=1e-12)
    assert np.allclose(P.conj().T, P, atol=1e-12)


def test_s_is_unitary() -> None:
    """Sanity: exp(iH) for Hermitian H is unitary."""
    _, _, S = _build_inputs()
    n = S.shape[0]
    assert np.allclose(S.conj().T @ S, np.eye(n), atol=1e-10)


def test_unitarity_closure_on_h_phys() -> None:
    """P · S† · S · P  =  P  to numerical precision."""
    P, _, S = _build_inputs()
    lhs = P @ S.conj().T @ S @ P
    residual = np.linalg.norm(lhs - P)
    assert residual < 1e-10, f"Unitarity residual on H_phys: {residual:.3e}"


@pytest.mark.parametrize("seed", [1, 2, 3, 17, 42])
def test_unitarity_closure_seed_sweep(seed: int) -> None:
    P, _, S = _build_inputs(seed=seed)
    lhs = P @ S.conj().T @ S @ P
    assert np.linalg.norm(lhs - P) < 1e-10


def test_bootstrap_partial_wave_bound() -> None:
    """All eigenvalues of `P S P` have modulus ≤ 1."""
    P, _, S = _build_inputs()
    eig = np.linalg.eigvals(P @ S @ P)
    assert np.max(np.abs(eig)) <= 1.0 + 1e-10


def test_fakeon_block_is_real() -> None:
    """(I − P) · T · (I − P) has zero imaginary part."""
    P, T, _ = _build_inputs()
    Q = np.eye(P.shape[0]) - P
    fakeon = Q @ T @ Q
    assert np.max(np.abs(fakeon.imag)) < 1e-12


def test_t_matrix_is_hermitian() -> None:
    """The synthetic T is Hermitian (matches the optical-theorem hypothesis)."""
    _, T, _ = _build_inputs()
    assert np.allclose(T, T.conj().T, atol=1e-12)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
