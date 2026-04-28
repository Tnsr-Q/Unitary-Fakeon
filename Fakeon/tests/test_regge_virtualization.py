"""tests/test_regge_virtualization.py — Regge-pole certificate hooks."""

from __future__ import annotations

import numpy as np
import pytest

from fakeon_numeric.regge_solver import (
    ReggeCertificate,
    find_regge_root,
    scan_regge_trajectory,
    verify_fakeon_virtualization,
)
from fakeon_numeric.tolerance_ledger import update_ledger


def test_find_regge_root_converges() -> None:
    nu = find_regge_root(t=1.0)
    # Toy model: α(1) = -1.3 + 0.05i.
    assert abs(nu.real + 1.3) < 1e-9
    assert abs(nu.imag - 0.05) < 1e-9


@pytest.mark.parametrize("t", [0.1, 1.0, 5.0, 100.0])
def test_re_alpha_negative_for_positive_t(t: float) -> None:
    nu = find_regge_root(t=t)
    assert nu.real < 0.0


def test_scan_regge_trajectory_shape() -> None:
    t = np.linspace(0.1, 50.0, 17)
    traj = scan_regge_trajectory(t)
    assert traj.shape == t.shape
    assert traj.dtype == complex
    assert np.all(traj.real < 0.0)


def test_fakeon_virtualization_certificate() -> None:
    t = np.linspace(0.1, 200.0, 256)
    traj = scan_regge_trajectory(t)
    cert = verify_fakeon_virtualization(traj, t, M2_sq=10.0)
    assert isinstance(cert, ReggeCertificate)
    assert cert.fakeon_virtualized
    assert cert.re_alpha_at_M2 < 0.0
    update_ledger("regge_certificate",
                  cert.re_alpha_at_M2, cert.fakeon_virtualized)


def test_certificate_hash_is_deterministic() -> None:
    t = np.linspace(0.1, 50.0, 32)
    traj = scan_regge_trajectory(t)
    a = verify_fakeon_virtualization(traj, t, 10.0)
    b = verify_fakeon_virtualization(traj, t, 10.0)
    assert a.certificate_hash == b.certificate_hash


def test_certificate_hash_changes_when_trajectory_changes() -> None:
    t = np.linspace(0.1, 50.0, 32)
    traj = scan_regge_trajectory(t)
    perturbed = traj + 1e-3
    a = verify_fakeon_virtualization(traj, t, 10.0)
    b = verify_fakeon_virtualization(perturbed, t, 10.0)
    assert a.certificate_hash != b.certificate_hash


def test_certificate_dict_has_status_field() -> None:
    t = np.linspace(0.1, 100.0, 64)
    traj = scan_regge_trajectory(t)
    d = verify_fakeon_virtualization(traj, t, 25.0).to_dict()
    assert d["status"] == "VERIFIED"
    assert d["fakeon_virtualized"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
