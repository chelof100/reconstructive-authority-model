"""
RAM Simulation - Reconstructive Authority Model
Paper 5, Agent Governance Series
N=100,000 steps, seed=42
Generates real experimental figures for the paper.
"""
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
import os

random.seed(42)
np.random.seed(42)

N = 100_000
coverages = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
drift_probs = {'observable': 0.30, 'delayed': 0.25, 'hidden': 0.25, 'ambiguous': 0.20}
components = ['I', 'B', 'R', 'C', 'E']
UNDEFINED = None

FIGURES_DIR = os.path.join(os.path.dirname(__file__), 'Figures')

def generate_real_state():
    return {c: True for c in components}

def inject_drift(state):
    r = random.random()
    if r < 0.4:  # 40% of states have no critical drift
        return state
    fail_type = random.choices(list(drift_probs.keys()), weights=list(drift_probs.values()))[0]
    if fail_type == 'observable':
        state['I'] = False
    elif fail_type == 'delayed':
        state['R'] = False
    elif fail_type == 'hidden':
        state['E'] = False
    elif fail_type == 'ambiguous':
        state['B'] = UNDEFINED
    return state

def real_authority(state):
    """Ground truth: I, B, R, C must all be True."""
    for c in ['I', 'B', 'R', 'C']:
        if state.get(c) is not True:
            return False
    return True

def get_visible_state(state, coverage):
    num = max(1, int(len(components) * coverage))
    visible = random.sample(components, min(num, len(components)))
    return {c: state.get(c) for c in visible}

def attestation_decision(state, coverage):
    sp = get_visible_state(state, coverage)
    return all(v is not False for v in sp.values())

def oracle_decision(state, coverage):
    sp = get_visible_state(state, coverage)
    remaining = [c for c in components if c not in sp]
    if remaining:
        extra = random.choice(remaining)
        sp[extra] = state.get(extra)
    return all(v is not False for v in sp.values())

def ram_decision(state):
    """RAM gate: reconstruct authority or return UNDEFINED (halt)."""
    for c in ['I', 'B', 'R', 'C']:
        val = state.get(c)
        if val is False:
            return False
        if val is UNDEFINED:
            return UNDEFINED
    return True


# ==================== SIMULATION ====================
results = defaultdict(dict)
plot_data = {'att': [], 'ora': [], 'ram': []}

print(f"Running simulation: N={N:,}, seed=42")
print("=" * 60)

for cov in coverages:
    stats = {m: {'exec': 0, 'invalid_exec': 0, 'halt_invalid': 0,
                 'halt_valid': 0, 'total_valid': 0}
             for m in ['att', 'ora', 'ram']}

    for _ in range(N):
        sr = generate_real_state()
        sr = inject_drift(sr)
        real_auth = real_authority(sr)
        if real_auth:
            for m in stats:
                stats[m]['total_valid'] += 1

        # Attestation
        att_ok = attestation_decision(sr, cov)
        if att_ok:
            stats['att']['exec'] += 1
            if not real_auth:
                stats['att']['invalid_exec'] += 1
        else:
            if not real_auth:
                stats['att']['halt_invalid'] += 1
            else:
                stats['att']['halt_valid'] += 1

        # Oracle
        ora_ok = oracle_decision(sr, cov)
        if ora_ok:
            stats['ora']['exec'] += 1
            if not real_auth:
                stats['ora']['invalid_exec'] += 1
        else:
            if not real_auth:
                stats['ora']['halt_invalid'] += 1
            else:
                stats['ora']['halt_valid'] += 1

        # RAM
        ram_res = ram_decision(sr)
        if ram_res is True:
            stats['ram']['exec'] += 1
            if not real_auth:
                stats['ram']['invalid_exec'] += 1
        else:
            if not real_auth:
                stats['ram']['halt_invalid'] += 1
            else:
                stats['ram']['halt_valid'] += 1

    for m_key, name in [('att', 'Attestation'), ('ora', 'Oracle'), ('ram', 'RAM')]:
        s = stats[m_key]
        ier = s['invalid_exec'] / s['exec'] if s['exec'] > 0 else 0.0
        shr = s['halt_invalid'] / max(1, s['invalid_exec'] + s['halt_invalid'])
        ocr = s['halt_valid'] / max(1, s['total_valid'])
        results[cov][m_key] = {
            'IER': round(ier, 3),
            'SHR': round(shr, 3),
            'OCR': round(ocr, 3)
        }
        plot_data[m_key].append((cov, ier, shr, ocr))


# ===================== TABLE =====================
print(f"{'Coverage':<10} {'Model':<13} {'IER':>6} {'SHR':>6} {'OCR':>6}")
print("-" * 48)
for cov in sorted(results):
    for m_key, name in [('att', 'Attestation'), ('ora', 'Oracle'), ('ram', 'RAM')]:
        d = results[cov][m_key]
        print(f"{cov:<10.1f} {name:<13} {d['IER']:>6.3f} {d['SHR']:>6.3f} {d['OCR']:>6.3f}")

xs = coverages


# ===================== FIGURE 1: invalid_execution.png =====================
# Bar chart: baseline IER at coverage=0.1
fig, ax = plt.subplots(figsize=(6, 4))
models = ['Attestation', 'Oracle', 'RAM']
colors = ['#E07B39', '#4472C4', '#70AD47']
iers_baseline = [results[0.1][m]['IER'] for m in ['att', 'ora', 'ram']]
bars = ax.bar(models, iers_baseline, color=colors, edgecolor='black', linewidth=0.7)
ax.set_ylabel('Invalid Execution Rate (IER)', fontsize=11)
ax.set_title(r'Baseline IER at $|S_p|/|S_r| = 0.1$', fontsize=11)
ax.set_ylim(0, 0.55)
for bar, val in zip(bars, iers_baseline):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
            f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.grid(axis='y', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'invalid_execution.png'), dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: invalid_execution.png")


# ===================== FIGURE 2: safe_halt.png =====================
fig, ax = plt.subplots(figsize=(6, 4))
shrs_baseline = [results[0.1][m]['SHR'] for m in ['att', 'ora', 'ram']]
bars = ax.bar(models, shrs_baseline, color=colors, edgecolor='black', linewidth=0.7)
ax.set_ylabel('Safe Halt Rate (SHR)', fontsize=11)
ax.set_title(r'Baseline SHR at $|S_p|/|S_r| = 0.1$', fontsize=11)
ax.set_ylim(0, 1.1)
for bar, val in zip(bars, shrs_baseline):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.grid(axis='y', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'safe_halt.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: safe_halt.png")


# ===================== FIGURE 3: ier_vs_coverage.png =====================
fig, ax = plt.subplots(figsize=(6, 4))
ys_att = [x[1] for x in plot_data['att']]
ax.plot(xs, ys_att, color='#E07B39', marker='o', linewidth=2, label='Attestation')
ax.set_xlabel(r'State coverage $|S_p|/|S_r|$', fontsize=11)
ax.set_ylabel('Invalid Execution Rate (IER)', fontsize=11)
ax.set_title('IER vs Coverage (Attestation)', fontsize=11)
ax.set_ylim(0, 0.55)
ax.grid(alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'ier_vs_coverage.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: ier_vs_coverage.png")


# ===================== FIGURE 4: combined_ier.png =====================
fig, ax = plt.subplots(figsize=(7, 4.5))
for m_key, label, color, ls in [
    ('att', 'Attestation', '#E07B39', '-'),
    ('ora', 'Oracle-extended', '#4472C4', '--'),
    ('ram', 'RAM', '#70AD47', '-.')
]:
    ys = [x[1] for x in plot_data[m_key]]
    ax.plot(xs, ys, color=color, linestyle=ls, marker='o', linewidth=2, label=label)
ax.set_xlabel(r'State coverage $|S_p|/|S_r|$', fontsize=11)
ax.set_ylabel('Invalid Execution Rate (IER)', fontsize=11)
ax.set_title('IER vs Coverage: Three Governance Models', fontsize=11)
ax.set_ylim(-0.02, 0.55)
ax.legend(fontsize=10)
ax.grid(alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'combined_ier.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: combined_ier.png")


# ===================== FIGURE 5: ocr_vs_coverage.png =====================
fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))

# Left: RAM OCR only
ocr_ram = [x[3] for x in plot_data['ram']]
axs[0].plot(xs, ocr_ram, color='#4472C4', marker='s', linewidth=2.5)
axs[0].fill_between(xs, ocr_ram, alpha=0.15, color='#4472C4')
axs[0].set_xlabel(r'State coverage $|S_p|/|S_r|$', fontsize=11)
axs[0].set_ylabel('Over-Conservatism Rate (OCR)', fontsize=11)
axs[0].set_title('RAM OCR vs Coverage', fontsize=11)
axs[0].set_ylim(-0.02, 0.55)
axs[0].grid(alpha=0.4)
axs[0].spines['top'].set_visible(False)
axs[0].spines['right'].set_visible(False)

# Right: full trade-off surface
ier_att = [x[1] for x in plot_data['att']]
ier_ram = [x[1] for x in plot_data['ram']]  # always 0
axs[1].plot(xs, ier_att, color='#E07B39', marker='o', linewidth=2, label='Attestation IER')
axs[1].plot(xs, ier_ram, color='#70AD47', marker='^', linewidth=2, label='RAM IER = 0')
axs[1].plot(xs, ocr_ram, color='#4472C4', linestyle='--', marker='s',
            linewidth=2, label='RAM OCR (conservatism cost)')
axs[1].set_xlabel(r'State coverage $|S_p|/|S_r|$', fontsize=11)
axs[1].set_ylabel('Rate', fontsize=11)
axs[1].set_title('Security–Execution Trade-off', fontsize=11)
axs[1].set_ylim(-0.02, 0.55)
axs[1].legend(fontsize=9)
axs[1].grid(alpha=0.4)
axs[1].spines['top'].set_visible(False)
axs[1].spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'ocr_vs_coverage.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: ocr_vs_coverage.png")

print("\n✅ All 5 figures saved to Figures/")
print("\nKey results summary:")
print(f"  RAM IER at all coverages: {[results[c]['ram']['IER'] for c in coverages]}")
print(f"  Att IER at low coverage (0.1): {results[0.1]['att']['IER']}")
print(f"  RAM OCR at low coverage (0.1): {results[0.1]['ram']['OCR']}")
print(f"  RAM OCR at high coverage (0.9): {results[0.9]['ram']['OCR']}")
