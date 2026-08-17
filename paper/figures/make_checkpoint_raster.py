import glob
import json
import csv
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

D = '/home/zihanz/waterhedron_benchmark_blind/paper/checkpoint_profiles'
FIG = '/home/zihanz/waterhedron_benchmark_blind/paper/figures'
MAE_CSV = FIG + '/checkpoint_formula_mae.csv'

plt.rcParams.update({
    'font.size': 14,
    'legend.fontsize': 14,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'text.usetex': True,
    'font.family': 'serif',
    'text.latex.preamble': r'\usepackage{amsmath}',
})

modmap = {'claude_opus_48_max':'Claude max','claude_opus_48_ultra':'Claude ultra',
          'codex_54_xhigh':'Codex 5.4','codex_55_xhigh':'Codex 5.5',
          'deepseek_v4_pro':'DeepSeek','fugu_ultra':'Fugu'}
modorder = ['claude_opus_48_max','claude_opus_48_ultra','codex_54_xhigh',
            'codex_55_xhigh','deepseek_v4_pro','fugu_ultra']
prof = {}
for f in glob.glob(D + '/*.json'):
    d = json.load(open(f)); prof[d['run']] = d

mae = {}
with open(MAE_CSV, newline='') as handle:
    for row in csv.DictReader(handle):
        value = row['mae_phi8'].strip()
        mae[row['run']] = None if not value else float(value)

Ks = ['K1','K2','K3','K4','K5','K6','K7','K8']
Klab = [r'$K_1$ exact values', r'$K_2$ fixed properties',
        r'$K_3$ principal formula', r'$K_4$ failed test',
        r'$K_5$ chamber formulas', r'$K_6$ every boundary',
        r'$K_7$ complete formula', r'$K_8$ new chambers']
statuscol = {'reached':'#1f4e79','partial':'#9dc3e6','not':'#f2f2f2'}
outcol = {'global':'#2E7D32','near':'#EF8A17','local':'#2B6CB0','reject':'#7B3FA1','incorrect':'#666666'}
outlet = {'global':'C','near':'P','local':'O','reject':'R','incorrect':'I'}

expected_runs = {
    f'{case}/{model}'
    for case in ['case_1', 'case_2', 'case_3']
    for model in modorder
}
if set(prof) != expected_runs:
    missing = sorted(expected_runs - set(prof))
    extra = sorted(set(prof) - expected_runs)
    raise ValueError(f'checkpoint profile mismatch: missing={missing}, extra={extra}')
if set(mae) != expected_runs:
    missing = sorted(expected_runs - set(mae))
    extra = sorted(set(mae) - expected_runs)
    raise ValueError(f'MAE table mismatch: missing={missing}, extra={extra}')

for run, d in prof.items():
    bad_statuses = {
        k: d['checkpoints'].get(k)
        for k in Ks
        if d['checkpoints'].get(k) not in statuscol
    }
    if bad_statuses:
        raise ValueError(f'invalid checkpoint status for {run}: {bad_statuses}')
    if d['final_outcome'] not in outcol:
        raise ValueError(f"invalid outcome for {run}: {d['final_outcome']}")

rows = []
for c in ['case_1','case_2','case_3']:
    for m in modorder:
        rows.append((c, m, prof[f'{c}/{m}']))
n = len(rows)

fig, ax = plt.subplots(figsize=(10.5, 8.6))
OX = len(Ks) + 0.35  # outcome column x
MX = OX + 1.35       # MAE column x

def format_mae(value):
    if value is None:
        return r'\textemdash'
    if math.isclose(value, 0.0, abs_tol=1e-12):
        return r'$0$'
    if value < 0.01:
        return rf'${value:.4f}$'
    if value < 1000:
        return rf'${value:.2f}$'
    exponent = math.floor(math.log10(value))
    mantissa = value / 10**exponent
    return rf'${mantissa:.2f}\mathrm{{e}}{exponent}$'

for i, (c, m, d) in enumerate(rows):
    y = n - 1 - i
    for j, k in enumerate(Ks):
        st = d['checkpoints'].get(k, 'not')
        ax.add_patch(Rectangle((j, y), 0.9, 0.9, facecolor=statuscol[st], edgecolor='white', lw=1.6))
    o = d['final_outcome']
    ax.add_patch(Rectangle((OX, y), 0.9, 0.9, facecolor=outcol[o], edgecolor='white', lw=1.6))
    ax.text(OX + 0.45, y + 0.45, outlet[o], ha='center', va='center', color='white', fontsize=14, fontweight='bold')
    ax.add_patch(Rectangle((MX, y), 1.18, 0.9, facecolor='#fafafa', edgecolor='white', lw=1.6))
    ax.text(MX + 0.59, y + 0.45, format_mae(mae[d['run']]),
            ha='center', va='center', color='#222222', fontsize=13)
    ax.text(-0.25, y + 0.45, modmap[m], ha='right', va='center', fontsize=14)

for j, kl in enumerate(Klab):
    ax.text(j + 0.35, n + 0.15, kl, ha='left', va='bottom', rotation=45, fontsize=14)
ax.text(OX + 0.2, n + 0.15, 'result', ha='left', va='bottom', rotation=45, fontsize=14)
ax.text(MX + 0.22, n + 0.15, r'$\mathrm{MAE}_8(\Phi_8)$',
        ha='left', va='bottom', rotation=45, fontsize=14)

for gi in [6, 12]:
    yy = n - gi
    ax.plot([-3.05, MX + 1.28], [yy, yy], color='black', lw=1.0)
for cond, gi in [('false hint', 3), ('true hint', 9), ('no hint', 15)]:
    ax.text(-3.25, n - gi + 0.45, cond, ha='center', va='center', rotation=90, fontsize=14, fontweight='bold')

ax.set_xlim(-3.5, MX + 1.42)
ax.set_ylim(-0.9, n + 2.4)
ax.axis('off')
leg = [Patch(facecolor=statuscol['reached'], label='complete'),
       Patch(facecolor=statuscol['partial'], label='partly complete'),
       Patch(facecolor=statuscol['not'], label='not reached')]
ax.legend(handles=leg, loc='lower center', bbox_to_anchor=(0.42, -0.02), ncol=3, frameon=False)
plt.tight_layout()
plt.savefig(FIG + '/checkpoint_raster.pdf', bbox_inches='tight')
print('saved checkpoint_raster.pdf with checkpoint_formula_mae.csv')
