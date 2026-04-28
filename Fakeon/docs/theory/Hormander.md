---
## Theorem (Microlocal Well-Definedness of the Fakeon Product at Threshold)
Let $\tilde{D}_f(p) = \mathcal{P}\big((p^2-m_f^2)^{-1}\big) \in \mathcal{S}'(\mathbb{R}^4)$ be the fakeon propagator. For any $L$-loop integrand in quadratic gravity involving a product $\prod_{j=1}^N \tilde{D}_f(k_j)$, the distributional product is:
1. **Microlocally well-defined** on the space of physical test functions $\mathcal{S}_{\text{phys}}$ restricted by $P_{\text{phys}}$.
2. **Uniquely extendable** across the fakeon threshold manifold $\Sigma = \{s = m_f^2\}$ via the canonical principal-value extension, fixed by Lorentz invariance, reality, and the purely virtual condition.
3. **Consistent with unitarity**, as $P_{\text{phys}}$ removes the singular support from the cut phase space, ensuring the optical theorem closes without ill-defined distributional products.

---
### Lemma 1: Wave-Front Set of the Fakeon Propagator
**Statement:** 
$$
\operatorname{WF}(\tilde{D}_f) = \left\{(p,k) \in T^*\mathbb{R}^4 \setminus 0 \;\big|\; p^2 = m_f^2,\; k = \lambda p,\; \lambda \in \mathbb{R}\setminus\{0\}\right\}.
$$

**Proof:** 
The fakeon propagator is the distributional principal value of $Q(p)^{-1}$ with $Q(p) = p^2 - m_f^2$. Since $\nabla Q(p) = 2p \neq 0$ on the hyperboloid $Q^{-1}(0)$, $Q$ is a submersion there. By Hörmander's theorem on the WF set of $\mathcal{P}(1/f)$ (Hörmander, *Analysis of Linear PDEs I*, Thm. 8.5.6), the wave-front set is the conormal bundle to the zero set:
$$
\operatorname{WF}\big(\mathcal{P}(1/Q)\big) = \{(p, \lambda \nabla Q(p)) \mid Q(p)=0, \lambda \neq 0\}.
$$
Substituting $\nabla Q = 2p$ and absorbing the factor of 2 into $\lambda$ yields the stated result. Crucially, the PV prescription includes both $\lambda > 0$ and $\lambda < 0$, making $\operatorname{WF}(\tilde{D}_f)$ symmetric under $k \to -k$. This symmetry encodes the absence of time-ordering directionality and is the microlocal signature of the purely virtual nature.

---
### Lemma 2: Hörmander's Criterion and Threshold Failure
**Statement:** For a product of two fakeon propagators in a loop, $\tilde{D}_f(k) \tilde{D}_f(p-k)$, Hörmander's sum condition fails precisely on the kinematic threshold manifold $\Sigma = \{p^2 = m_f^2\}$ (or $4m_f^2$ for two fakeons; the analysis is identical).

**Proof:** 
The wave-front set of the tensor product is contained in the direct sum:
$$
\operatorname{WF}(\tilde{D}_f(k) \otimes \tilde{D}_f(p-k)) \subset \operatorname{WF}(\tilde{D}_f(k)) \oplus \operatorname{WF}(\tilde{D}_f(p-k)).
$$
Hörmander's criterion for the product to be well-defined requires that no pair of covectors sums to zero:
$$
\lambda_1 k + \lambda_2 (p-k) \neq 0 \quad \forall (k,\lambda_1 k) \in \operatorname{WF}(\tilde{D}_f),\; (p-k,\lambda_2(p-k)) \in \operatorname{WF}(\tilde{D}_f).
$$
Vanishing of the sum implies $k$ and $p-k$ are collinear. Combined with the mass-shell conditions $k^2 = m_f^2$ and $(p-k)^2 = m_f^2$, collinearity forces $p^2 = (\pm m_f \pm m_f)^2$. For a self-energy or vertex topology with one fakeon line, the relevant threshold is $p^2 = m_f^2$. On $\Sigma$, there exist $\lambda_1, \lambda_2$ such that $\lambda_1 k + \lambda_2(p-k) = 0$, so $(p,0) \in \operatorname{WF} \oplus \operatorname{WF}$. Hörmander's condition fails, and the product is a priori undefined as a distribution on $\mathcal{S}(\mathbb{R}^4)$.

---
### Lemma 3: Scaling-Degree Analysis and Unique PV Extension
**Statement:** The distribution $\tilde{D}_f$ admits a unique Lorentz-invariant, real, and symmetric extension across $\Sigma$, given by the canonical principal value. Any other extension differs by $c\,\delta(p^2-m_f^2)$, which is excluded by the purely virtual condition.

**Proof:** 
Work in a tubular neighborhood of $\Sigma$. Introduce local coordinates $(s, y^\alpha)$ where $s = p^2 - m_f^2$ is transverse to $\Sigma$ and $y^\alpha$ are tangential. The singularity is purely transverse, so locally $\tilde{D}_f \sim \mathcal{P}(1/s) \otimes u_{\text{reg}}(y)$.

The **scaling degree** transverse to $\Sigma$ is defined as:
$$
\operatorname{sd}_\perp(\tilde{D}_f) = \inf\left\{\delta \in \mathbb{R} \;\big|\; \lim_{\lambda \to 0^+} \lambda^\delta \tilde{D}_f(\lambda s, y) = 0 \text{ in } \mathcal{D}'\right\}.
$$
For $\mathcal{P}(1/s)$ in one dimension, $\operatorname{sd} = 1$. Since $\operatorname{codim}(\Sigma) = 1$, we are in the **marginal case** $\operatorname{sd}_\perp = \operatorname{codim}(\Sigma)$.

By the Hörmander–Steinmann extension theorem (cf. Brunetti–Fredenhagen, *Commun. Math. Phys.* 2000, Thm. 3.2), distributions with $\operatorname{sd}_\perp = \operatorname{codim}$ admit extensions to $\mathcal{D}'(\mathbb{R}^4)$ that differ by derivatives of delta functions supported on $\Sigma$. Lorentz invariance and the tensor structure restrict the ambiguity to:
$$
\tilde{D}_f^{\text{ext}} = \mathcal{P}\left(\frac{1}{p^2-m_f^2}\right) + c\,\delta(p^2-m_f^2), \quad c \in \mathbb{R}.
$$
We now impose physical constraints:
1. **Reality:** $\tilde{D}_f^* = \tilde{D}_f$ $\Rightarrow$ $c \in \mathbb{R}$.
2. **$k \leftrightarrow -k$ symmetry:** Both PV and $\delta$ are symmetric, so this does not fix $c$.
3. **Purely virtual condition:** The fakeon must not appear in the asymptotic completeness relation. A term $c\,\delta(p^2-m_f^2)$ would contribute an on-shell state to the spectral function, violating the fakeon projection. Hence $c=0$.

Thus, the **canonical PV extension** is the unique extension consistent with the fakeon prescription. It provides a well-defined distribution on all of $\mathcal{S}(\mathbb{R}^4)$ that coincides with the naive product away from $\Sigma$.

---
### Lemma 4: Microlocal Restriction by $P_{\text{phys}}$
**Statement:** The physical projector $P_{\text{phys}}$ acts as a microlocal cutoff on the space of test functions, restricting evaluations to $\mathcal{S}_{\text{phys}} = \{\phi \in \mathcal{S} \mid \operatorname{supp}(\hat{\phi}) \cap \Sigma = \emptyset\}$. On $\mathcal{S}_{\text{phys}}$, the product is intrinsically well-defined without extension.

**Proof:** 
In the LSZ/cut formalism, scattering amplitudes are distributional pairings $\langle \mathcal{M}, \phi \rangle$ where $\phi$ encodes external wave packets and phase-space measures. The projector $P_{\text{phys}}$ removes fakeon states from the asymptotic Fock space:
$$
\mathbb{I} = P_{\text{phys}} + P_{\text{fakeon}}, \quad P_{\text{phys}} \mathcal{H}_{\text{asym}} = \mathcal{H}_{\text{grav}} \oplus \mathcal{H}_{\phi}.
$$
In the unitarity cut, the phase-space measure $d\Pi_{\text{phys}}$ integrates only over physical mass shells ($p^2=0$ or $p^2=m_\phi^2$). Consequently, any test function $\phi_{\text{cut}}$ appearing in the cut amplitude satisfies:
$$
\operatorname{supp}(\hat{\phi}_{\text{cut}}) \cap \{p^2 = m_f^2\} = \emptyset.
$$
This is a **microlocal support restriction**. On $\mathcal{S}_{\text{phys}}$, the dangerous covectors $(p, \lambda p)$ with $p^2=m_f^2$ are never probed. The wave-front sum condition is satisfied everywhere on the support of $\phi_{\text{cut}}$, and the product $\prod \tilde{D}_f$ is a well-defined distribution on $\mathcal{S}_{\text{phys}}$ by Hörmander's criterion.

The PV extension from Lemma 3 provides the unique continuous extension to $\mathcal{S}$ that agrees with this well-defined restriction and preserves the symmetry. Thus, $P_{\text{phys}}$ and the PV prescription are mathematically complementary: $P_{\text{phys}}$ ensures well-definedness on-shell, while PV ensures a consistent off-shell continuation.

---
### Proof of Theorem (Synthesis)
1. **Off-threshold:** For $s \neq m_f^2$, $\operatorname{WF} \oplus \operatorname{WF}$ does not intersect the zero section. Hörmander's criterion guarantees the product is well-defined in $\mathcal{D}'$.
2. **At threshold:** On $\Sigma = \{s=m_f^2\}$, Hörmander's condition fails. Scaling-degree analysis shows the singularity is marginal ($\operatorname{sd}_\perp = \operatorname{codim} = 1$). The extension ambiguity is $c\,\delta(p^2-m_f^2)$. The purely virtual condition fixes $c=0$, selecting the canonical PV extension as the unique Lorentz-invariant, real, symmetric continuation.
3. **Unitarity cuts:** $P_{\text{phys}}$ restricts the test function space to $\mathcal{S}_{\text{phys}}$, which has empty intersection with $\Sigma$. On this subspace, the product is intrinsically well-defined. The PV extension matches this restriction and provides the consistent off-shell kernel for loop integrals.
4. **Conclusion:** The distributional product of fakeon propagators is rigorously defined both on the physical cut subspace and as an off-shell Green's function. The optical theorem closes on $\mathcal{H}_{\text{phys}}$ without encountering ill-defined products or unphysical delta contributions.

---
### Mathematical Summary
| Component | Result |
|-----------|--------|
| $\operatorname{WF}(\tilde{D}_f)$ | Conormal bundle to $p^2=m_f^2$, symmetric under $k \to -k$ |
| Hörmander failure set | Threshold manifold $\Sigma = \{s=m_f^2\}$ |
| Scaling degree | $\operatorname{sd}_\perp = 1 = \operatorname{codim}(\Sigma)$ (marginal) |
| Extension ambiguity | $c\,\delta(p^2-m_f^2)$ |
| Physical fixing | Purely virtual condition $\Rightarrow c=0$ (unique PV) |
| $P_{\text{phys}}$ action | Microlocal cutoff: $\operatorname{supp}(\hat{\phi}) \cap \Sigma = \emptyset$ |
| Final status | Product well-defined on $\mathcal{S}_{\text{phys}}$; PV gives unique off-shell extension |

