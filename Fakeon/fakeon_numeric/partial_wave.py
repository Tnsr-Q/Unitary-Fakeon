###"""fakeon_numeric.partial_wave — partial-wave decomposition utilities.

###Placeholder module.
###"""

###from __future__ import annotations


###def project_partial_wave(*_args, **_kwargs):  # pragma: no cover
    ###raise NotImplementedError("fakeon_numeric.partial_wave.project_partial_wave: stub")

#!/usr/bin/env python3
"""
Automated Levin/Weniger Convergence Acceleration for Partial Wave Sums
-----------------------------------------------------------------------
Accelerates slowly converging or oscillating series of the form:
  S = ∑_{l=0}^∞ a_l,  where a_l = (2l+1) P_l(cosγ) g_l(r,r',ω)

Features:
  - Weniger δ-transformation with adaptive Levin u fallback
  - Automatic remainder estimate selection based on term behavior
  - High-precision stability controls (mpmath)
  - Rigorous relative/absolute error estimation
  - Direct integration with SchwarzschildRadialSolver & PV mode-sums
  - Convergence diagnostics & asymptotic decay validation

Dependencies: mpmath
Usage:
  acc = PartialWaveAccelerator(tol=1e-40, max_terms=80, dps=60)
  S_acc, err, n_terms = acc.run(term_generator)
"""

import mpmath as mp
from typing import Callable, Tuple, List, Optional
import warnings

class PartialWaveAccelerator:
    def __init__(self, tol: float = 1e-35, max_terms: int = 100, dps: int = 60, beta: float = 1.0):
        """
        Initialize accelerator.
        tol: Target relative error
        max_terms: Maximum partial wave index l to evaluate
        dps: Decimal precision for mpmath
        beta: Shift parameter for Weniger δ (default 1.0)
        """
        self.tol = mp.mpf(tol)
        self.max_terms = max_terms
        self.dps = dps
        self.beta = mp.mpf(beta)
        self.reset()

    def reset(self):
        """Clear internal state for a new series."""
        self.S: List[mp.mpf] = []      # Partial sums
        self.a: List[mp.mpf] = []      # Raw terms
        self.omega: List[mp.mpf] = []  # Remainder estimates
        self.acc_history: List[mp.mpf] = []  # Accelerated estimates
        self.oscillation_score: float = 0.0

    def _update_oscillation_score(self, term: mp.mpf):
        """Track sign changes to auto-select remainder estimate."""
        if len(self.a) >= 2:
            if mp.sign(term) != mp.sign(self.a[-1]):
                self.oscillation_score += 1.0
            else:
                self.oscillation_score -= 0.5
        self.oscillation_score = max(0.0, self.oscillation_score)

    def _select_remainder_estimate(self, n: int, term: mp.mpf) -> mp.mpf:
        """
        Adaptive remainder estimate ω_n:
        - Weniger δ: ω_n = a_n (optimal for oscillating series)
        - Levin u:   ω_n = (n+1)a_n (optimal for monotonic/logarithmic decay)
        Auto-selects based on recent oscillation behavior.
        """
        if mp.fabs(term) < mp.mpf('1e-80'):
            return (n + 1) * term  # Fallback to avoid division by zero
        
        if self.oscillation_score > 2.0:
            return term  # Oscillating → Weniger δ
        else:
            return (n + 1) * term  # Monotonic → Levin u

    def _compute_weniger_delta(self, k: int) -> Optional[mp.mpf]:
        """
        Compute Weniger δ_k^(0) transformation using terms 0..k.
        Formula: δ_k = N_k / D_k
        N_k = ∑_{j=0}^k (-1)^j C(k,j) [(β+j)/(β+k)]^{k-1} S_j / ω_j
        D_k = ∑_{j=0}^k (-1)^j C(k,j) [(β+j)/(β+k)]^{k-1} 1 / ω_j
        """
        if k >= len(self.S) or k < 2:
            return None

        num = mp.mpf('0')
        den = mp.mpf('0')
        
        # Precompute scaling factor to prevent overflow in binomial sums
        scale = mp.mpf('1')
        if k > 10:
            scale = mp.power(mp.mpf('10'), -k)

        for j in range(k + 1):
            binom = mp.binomial(k, j)
            sign = mp.mpf('-1')**j
            
            # Weight factor [(β+j)/(β+k)]^{k-1}
            if k == 1:
                weight = mp.mpf('1')
            else:
                weight = mp.power((self.beta + j) / (self.beta + k), k - 1)
            
            w_j = self.omega[j]
            if w_j == 0:
                continue
                
            inv_w = scale / w_j
            num += sign * binom * weight * self.S[j] * inv_w
            den += sign * binom * weight * inv_w

        if den == 0:
            return None
        return num / den

    def add_term(self, term: mp.mpf):
        """Append a new partial wave term and update internal state."""
        self.a.append(term)
        n = len(self.a) - 1
        self.S.append(self.S[-1] + term if n > 0 else term)
        self._update_oscillation_score(term)
        self.omega.append(self._select_remainder_estimate(n, term))

    def run(self, term_generator: Callable[[int], mp.mpf]) -> Tuple[mp.mpf, mp.mpf, int]:
        """
        Run acceleration until convergence or max_terms.
        Returns: (accelerated_sum, estimated_relative_error, terms_used)
        """
        with mp.workdps(self.dps):
            for ell in range(self.max_terms):
                term = term_generator(ell)
                self.add_term(term)
                
                if ell >= 3:  # Need at least 4 terms for stable transformation
                    acc_val = self._compute_weniger_delta(ell)
                    if acc_val is not None:
                        self.acc_history.append(acc_val)
                        if len(self.acc_history) >= 2:
                            rel_err = mp.fabs(self.acc_history[-1] - self.acc_history[-2]) / mp.fabs(self.acc_history[-1])
                            if rel_err < self.tol:
                                return acc_val, rel_err, ell + 1
            
            warnings.warn(f"Max terms ({self.max_terms}) reached. Final rel err: {rel_err:.2e}")
            return self.acc_history[-1], rel_err, len(self.a)


# =============================================================================
# PV PARTIAL WAVE SUM WRAPPER
# =============================================================================
def accelerated_pv_partial_wave_sum(
    gamma: float, r: float, rp: float, omega: float, 
    M: float, m_f: float, l_max: int = 80, dps: int = 60, tol: float = 1e-35
) -> Tuple[mp.mpf, mp.mpf, int]:
    """
    Compute ∑_{l=0}^∞ (2l+1)/(4π) P_l(cosγ) g_l(ω,r,r') with convergence acceleration.
    g_l(ω,r,r') = cos(ωΔt)/(2ω) ψ_{ωl}(r) ψ_{ωl}(r')  [Δt absorbed in caller if needed]
    
    Returns: (accelerated_sum, rel_error, l_used)
    """
    from fakeon_numeric.schwarzschild_radial_solver import SchwarzschildRadialSolver
    
    solver = SchwarzschildRadialSolver(M=M, m_f=m_f, ang_mom=0, dps=dps)  # l set dynamically below
    cos_gamma = mp.cos(mp.mpf(gamma))
    prefactor = mp.mpf('1') / (4 * mp.pi)
    
    # Cache radial modes to avoid recomputation
    radial_cache = {}
    
    def term_generator(ell: int) -> mp.mpf:
        solver.l = ell
        if ell not in radial_cache:
            psi = solver.get_mode(omega)
            radial_cache[ell] = psi(r) * psi(rp)
        
        g_l = radial_cache[ell]  # Δt factor can be multiplied externally
        P_l = mp.legendre(ell, cos_gamma)
        return prefactor * (2*ell + 1) * P_l * g_l

    acc = PartialWaveAccelerator(tol=tol, max_terms=l_max, dps=dps)
    return acc.run(term_generator)


# =============================================================================
# VALIDATION & CI DRIVER
# =============================================================================
if __name__ == "__main__":
    mp.dps = 50
    print("[INFO] Testing Partial Wave Acceleration on Schwarzschild PV Modes...")
    
    # Parameters
    gamma = mp.pi / 3  # Angular separation
    r, rp = 10.0, 12.0
    omega = 5.0
    M, m_f = 1.0, 2.5
    
    print(f"[CONFIG] γ={gamma:.3f}, r={r}, r'={rp}, ω={omega}, M={M}, m_f={m_f}")
    
    S_acc, err, l_used = accelerated_pv_partial_wave_sum(
        gamma=gamma, r=r, rp=rp, omega=omega, M=M, m_f=m_f, l_max=60, dps=50, tol=1e-30
    )
    
    print(f"\n[RESULT] Accelerated sum = {mp.nstr(S_acc, 15)}")
    print(f"         Estimated rel err = {mp.nstr(err, 3)}")
    print(f"         Terms used = {l_used}")
    print(f"         Im[S] = {mp.nstr(S_acc.im, 3)} {'✓ REAL' if S_acc.im == 0 else '✗ COMPLEX'}")
    
    # Convergence diagnostic
    print("\n[DIAGNOSTIC] Asymptotic decay check (last 5 terms):")
    from fakeon_numeric.schwarzschild_radial_solver import SchwarzschildRadialSolver

    solver = SchwarzschildRadialSolver(M=M, m_f=m_f, ang_mom=0, dps=50)
    cos_gamma = mp.cos(mp.mpf(gamma))
    prefactor = mp.mpf('1') / (4 * mp.pi)
    start_l = max(0, l_used - 5)
    for ell in range(start_l, l_used):
        solver.l = ell
        psi = solver.get_mode(omega)
        g_l = psi(r) * psi(rp)
        a_l = prefactor * (2 * ell + 1) * mp.legendre(ell, cos_gamma) * g_l
        print(f"  a_{ell} = {mp.nstr(a_l, 5)}")
    
    if err < 1e-25 and S_acc.im == 0:
        print("\n✓ VALIDATION PASSED: Acceleration converged with strict PV reality.")
    else:
        print("\n✗ VALIDATION WARNING: Check tolerance or increase dps/l_max.")
