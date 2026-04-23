# Reconstructive Authority Model (RAM) — Paper 5

**Paper 5 (operational closure) of the Agent Governance Series.**

> *Attestation guarantees that we measure correctly.*
> *RAM guarantees that what we measure is enough to act.*

---

## Paper

**Reconstructive Authority Model: Runtime Execution Validity Under Partial Observability**
Marcelo Fernandez (TraslaIA), 2026

DOI: [10.5281/zenodo.19669430](https://doi.org/10.5281/zenodo.19669430) &nbsp;|&nbsp; arXiv: [TBD]

---

## What this is

This repository contains the LaTeX source, Python simulation code, and experimental figures for **Paper 5** of the Agent Governance Series — the operational closure paper that answers the runtime question left open by Papers 0–4: *given that observability is incomplete and the architecture is irreducible, when should a system execute at all?*

**The core problem:** Existing governance frameworks rely on *attestation* — cryptographic proofs that computation was performed correctly on observed state. But attestation resolves *integrity* (was it computed correctly?), not *coverage* (was what was observed sufficient to justify the action?). These are different problems. RAM solves the second one.

**The key insight:**

> We separate integrity from coverage: authenticated projection is necessary, never sufficient.
> Our reconstruction gate reasons over an explicit coverage envelope (proven state, declared
> assumptions, unobservable residual) and permits execution only when coverage is adequate for
> that action class; otherwise it narrows privileges dynamically or fails closed.
> Attestation proves trust in measurement, not completeness of execution-relevant reality.

**The RAM model defines execution authority as a continuously derived property:**

```
A(t) = F(E(t), alpha)
```

where `E(t) = (S_p(t), H(t), delta(t))` is the *coverage envelope* — proven state, declared assumptions, and acknowledged unobservable residual. `F` returns: execute (`alpha`), narrow (`alpha' ⊊ alpha`), or halt (`false`/`undefined`).

**Core results:**
- **Theorem 1 (Attestation insufficiency):** No attestation-based system can guarantee execution validity w.r.t. real state `S_r(t)` unless authority is reconstructible from `S_r(t)` at runtime.
- **Theorem 2 (Necessity of RAM):** Reconstruction from `S_r(t)` is a *necessary* condition for execution validity guarantees.
- **Experimental:** RAM achieves IER = 0 at all coverage levels (N=100,000, seed=42). Attestation IER = 0.423 at low coverage, and critically, IER = 0.233 even at full coverage due to undefined-state handling failure.

**Appendix A** provides the complete constructive proof of Theorem 1 with Lemma A.1 (gap existence) and Lemma A.2 (execution-critical gap).

---

## Series position

| Paper | Question | Contribution |
|-------|----------|--------------|
| P0 — [Atomic Boundaries](https://github.com/chelof100/decision-boundary-model) | When is a decision atomic? | Atomic boundary theorem |
| P1 — [ACP](https://github.com/chelof100/acp-framework-en) | How to enforce the boundary? | Admission control protocol |
| P2 — [IML](https://github.com/chelof100/iml-benchmark) | What can be observed? | Observability impossibility result |
| P3/4 — [Governance Structure](https://github.com/chelof100/governance-structure) | Is governance structure irreducible? | Fair allocation + compositional irreducibility |
| **P5 — RAM (this paper)** | **Given all of the above, when to execute?** | **RAM + attestation necessity** |
| P6 — [Operationalizing RAM](https://github.com/chelof100/operationalizing-ram) | How is RAM enforced at runtime? | Runtime protocol + Recovery Loop |

RAM is the *operational closure* of the series: IML (P2) proves that full observability is unachievable; RAM provides the constructive response to that impossibility.

---

## Repository structure

```
reconstructive-authority-model/
├── Paper/
│   ├── main.tex                  # Full LaTeX source (26 pages)
│   ├── references.bib            # Bibliography
│   └── main.pdf                  # Compiled paper
├── Figures/
│   ├── combined_ier.png          # IER vs coverage: 3 models (real simulation)
│   ├── ier_vs_coverage.png       # IER vs coverage: attestation only
│   ├── invalid_execution.png     # Baseline IER bar chart
│   ├── safe_halt.png             # Baseline SHR bar chart
│   └── ocr_vs_coverage.png       # OCR trade-off surface
├── simulate_ram.py               # Python simulation (N=100,000, seed=42)
└── README.md
```

---

## Simulation

```bash
pip install numpy matplotlib
python simulate_ram.py
```

Runs N=100,000 steps with fixed seed=42. Generates all 5 figures and prints the full results table. Requires no external datasets.

**Key results (N=100,000, seed=42):**

| Coverage | Attestation IER | Oracle IER | RAM IER | RAM SHR |
|----------|----------------|------------|---------|---------|
| 0.1 | 0.423 | 0.393 | **0.000** | **1.000** |
| 0.5 | 0.394 | 0.354 | **0.000** | **1.000** |
| 0.9 | 0.302 | 0.232 | **0.000** | **1.000** |
| 1.0 | 0.233 | 0.233 | **0.000** | **1.000** |

Note: Attestation IER = 0.233 even at full coverage (|Sp|/|Sr| = 1.0) — the semantic failure from treating `UNDEFINED` state as benign.

---

## Cite

```bibtex
@misc{fernandez2026ram,
  author       = {Fernandez, Marcelo},
  title        = {Reconstructive Authority Model: Runtime Execution Validity
                 Under Partial Observability},
  year         = {2026},
  doi          = {10.5281/zenodo.19669430},
  howpublished = {\url{https://doi.org/10.5281/zenodo.19669430}},
  note         = {Agent Governance Series, Paper~5. Zenodo. DOI: 10.5281/zenodo.19669430}
}
```

---

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)
