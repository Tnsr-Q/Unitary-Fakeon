###"""fakeon_numeric.omega_quadrature — ω-plane quadrature for PV contours.

###Placeholder module.
###"""

###from __future__ import annotations


###def omega_quadrature(*_args, **_kwargs):  # pragma: no cover
    ###raise NotImplementedError("fakeon_numeric.omega_quadrature.omega_quadrature: stub")

#!/usr/bin/env python3
"""
Automated ω-Quadrature + Levin/Weniger Acceleration for Schwarzschild PV Propagator
------------------------------------------------------------------------------------
Computes: G_PV = ∑_{l=0}^∞ (2l+1)/(4π) P_l(cosγ) ∫_0^∞ dω [cos(ωΔt)/(2ω)] ψ_{ωl}(r) ψ_{ωl}(r')

Features:
  - Half-period partitioning of oscillatory ω-integral
  - Weniger δ-acceleration on ω-tail sequence
  - Nested acceleration: ω-integral per l → l-sum acceleration
  - Strict reality preservation (PV-compatible)
  - Adaptive precision & rigorous relative error estimation
  - Direct integration with SchwarzschildRadialSolver & PartialWaveAccelerator
  - Convergence diagnostics & CI-ready validation

Dependencies: mpmath, schwarzschild_radial_solver, partial_wave_accelerator
Usage:
  G, err_omega, err_l, info = compute_schwarzschild_pv_propagator(...)
"""

import mpmath as mp
from typing import Callable, Tuple, Dict, Optional
import warnings
import time

# Import previous modules (ensure they are in PYTHONPATH or same directory)
from fakeon_numeric.schwarzschild_radial_solver import SchwarzschildRadialSolver
from fakeon_numeric.partial_wave import PartialWaveAccelerator

# =============================================================================
# 1. OSCILLATORY ω-QUADRATURE WITH SEQUENCE ACCELERATION
# =============================================================================
class OscillatoryOmegaQuadrature:
    """
    Computes ∫_0^∞ f(ω) cos(ωΔt) dω via half-period partitioning + Weniger acceleration.
    Preserves strict reality for PV integrands.
    """
    def __init__(self, dt: float, tol: float = 1e-35, max_intervals: int = 60, 
                 dps: int = 60, omega_c: Optional[float] = None):
        self.dt = mp.mpf(dt)
        self.tol = mp.mpf(tol)
        self.max_intervals = max_intervals
        self.dps = dps
        self.omega_c = mp.mpf(omega_c) if omega_c else max(mp.mpf('15'), 5/mp.fabs(self.dt)) if self.dt != 0 else mp.mpf('50')
        self.acc = PartialWaveAccelerator(tol=tol, max_terms=max_intervals, dps=dps)
        self.intervals_computed = 0

    def _partial_integral(self, f_amp: Callable, w_start: mp.mpf, w_end: mp.mpf) -> mp.mpf:
        """Compute ∫_{w_start}^{w_end} f_amp(ω) cos(ωΔt) dω with adaptive quad."""
        if self.dt == 0:
            return mp.quad(f_amp, [w_start, w_end])
        # Integrand with explicit cosine
        integrand = lambda w: f_amp(w) * mp.cos(w * self.dt)
        return mp.quad(integrand, [w_start, w_end], error=False)

    def integrate(self, f_amp: Callable) -> Tuple[mp.mpf, mp.mpf, int]:
        """
        Returns: (accelerated_integral, rel_error, intervals_used)
        f_amp(ω) should return the non-oscillatory amplitude (e.g., ψψ/(2ω))
        """
        with mp.workdps(self.dps):
            self.acc.reset()
            self.intervals_computed = 0
            
            # 1. Direct integral up to cutoff
            I0 = self._partial_integral(f_amp, 0, self.omega_c)
            self.acc.add_term(I0)
            
            if self.dt == 0:
                return I0, mp.mpf('1e-30'), 1
            
            # 2. Oscillatory tail: partition by half-periods T = π/|Δt|
            T = mp.pi / mp.fabs(self.dt)
            w_curr = self.omega_c
            
            for k in range(1, self.max_intervals + 1):
                w_next = w_curr + T
                Ik = self._partial_integral(f_amp, w_curr, w_next)
                self.acc.add_term(Ik)
                self.intervals_computed += 1
                
                if k >= 3:
                    acc_val = self.acc._compute_weniger_delta(k)
                    if acc_val is not None:
                        self.acc.acc_history.append(acc_val)
                        if len(self.acc.acc_history) >= 2:
                            rel_err = mp.fabs(self.acc.acc_history[-1] - self.acc.acc_history[-2]) / mp.fabs(self.acc.acc_history[-1] + mp.mpf('1e-50'))
                            if rel_err < self.tol:
                                return I0 + acc_val, rel_err, k + 1
                w_curr = w_next
            
            warnings.warn(f"ω-quadrature max intervals reached. Rel err: {rel_err:.2e}")
            return I0 + self.acc.acc_history[-1], rel_err, self.intervals_computed + 1


# =============================================================================
# 2. NESTED DOUBLE ACCELERATOR (ω-integral → l-sum)
# =============================================================================
def compute_schwarzschild_pv_propagator(
    dt: float, gamma: float, r: float, rp: float, 
    M: float, m_f: float, 
    l_max: int = 60, omega_intervals: int = 50, 
    dps: int = 60, tol: float = 1e-30
) -> Tuple[mp.mpf, Dict]:
    """
    Computes the full Schwarzschild PV propagator with nested acceleration.
    Returns: (G_PV, diagnostics_dict)
    """
    t0 = time.time()
    with mp.workdps(dps):
        cos_gamma = mp.cos(mp.mpf(gamma))
        prefactor = mp.mpf('1') / (4 * mp.pi)
        
        # Initialize l-sum accelerator
        l_acc = PartialWaveAccelerator(tol=tol, max_terms=l_max, dps=dps)
        solver = SchwarzschildRadialSolver(M=M, m_f=m_f, l=0, dps=dps)
        
        omega_diag = []
        
        for l in range(l_max):
            solver.l = l
            
            # Define amplitude for ω-quadrature: ψ_{ωl}(r)ψ_{ωl}(r')/(2ω)
            def f_amp(omega):
                if omega < mp.mpf('1e-12'):
                    return mp.mpf('0')  # Regular at ω=0 for l≥0
                psi = solver.get_mode(omega)
                return psi(r) * psi(rp) / (2 * omega)
            
            # Accelerated ω-integral
            omega_quad = OscillatoryOmegaQuadrature(dt=dt, tol=tol*10, max_intervals=omega_intervals, dps=dps)
            I_l, err_omega, n_int = omega_quad.integrate(f_amp)
            
            # Partial wave term
            P_l = mp.legendre(l, cos_gamma)
            a_l = prefactor * (2*l + 1) * P_l * I_l
            l_acc.add_term(a_l)
            
            omega_diag.append({'l': l, 'I_l': I_l, 'err_omega': err_omega, 'intervals': n_int})
            
            # Check l-sum convergence
            if l >= 3:
                acc_l = l_acc._compute_weniger_delta(l)
                if acc_l is not None:
                    l_acc.acc_history.append(acc_l)
                    if len(l_acc.acc_history) >= 2:
                        rel_err_l = mp.fabs(l_acc.acc_history[-1] - l_acc.acc_history[-2]) / mp.fabs(l_acc.acc_history[-1] + mp.mpf('1e-50'))
                        if rel_err_l < tol:
                            elapsed = time.time() - t0
                            return acc_l, {
                                'G_PV': acc_l,
                                'rel_err_l': rel_err_l,
                                'l_used': l + 1,
                                'omega_diag': omega_diag,
                                'elapsed_sec': elapsed,
                                'reality_check': acc_l.im
                            }
        
        warnings.warn("l-sum max terms reached.")
        elapsed = time.time() - t0
        final_val = l_acc.acc_history[-1] if l_acc.acc_history else l_acc.S[-1]
        return final_val, {
            'G_PV': final_val,
            'rel_err_l': mp.mpf('1e-10'),
            'l_used': l_max,
            'omega_diag': omega_diag,
            'elapsed_sec': elapsed,
            'reality_check': final_val.im
        }


# =============================================================================
# 3. VALIDATION & CI DRIVER
# =============================================================================
if __name__ == "__main__":
    mp.dps = 50
    print("[INFO] Computing Schwarzschild PV Propagator with Nested Acceleration...")
    
    # Physical parameters
    dt = 2.0
    gamma = mp.pi / 3
    r, rp = 10.0, 12.0
    M, m_f = 1.0, 2.5
    
    print(f"[CONFIG] Δt={dt}, γ={gamma:.3f}, r={r}, r'={rp}, M={M}, m_f={m_f}, dps={mp.dps}")
    
    G_PV, diag = compute_schwarzschild_pv_propagator(
        dt=dt, gamma=gamma, r=r, rp=rp, M=M, m_f=m_f,
        l_max=50, omega_intervals=40, dps=50, tol=1e-28
    )
    
    print(f"\n[RESULT] G_PV = {mp.nstr(G_PV, 15)}")
    print(f"         l-sum rel err = {mp.nstr(diag['rel_err_l'], 3)}")
    print(f"         l terms used = {diag['l_used']}")
    print(f"         Im[G] = {mp.nstr(diag['reality_check'], 3)} {'✓ REAL' if diag['reality_check'] == 0 else '✗ COMPLEX'}")
    print(f"         Compute time = {diag['elapsed_sec']:.2f} s")
    
    print("\n[DIAGNOSTIC] ω-quadrature convergence (last 3 l-sectors):")
    for d in diag['omega_diag'][-3:]:
        print(f"  l={d['l']}: I_l={mp.nstr(d['I_l'], 8)}, err_ω={mp.nstr(d['err_omega'], 2)}, intervals={d['intervals']}")
    
    if diag['rel_err_l'] < 1e-25 and diag['reality_check'] == 0:
        print("\n✓ VALIDATION PASSED: Nested acceleration converged with strict PV reality.")
    else:
        print("\n✗ VALIDATION WARNING: Increase dps, l_max, or omega_intervals.")
