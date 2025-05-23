# %%
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

with open('dumps/llm/best_pncg.json') as f:
    baseline = json.load(f)

with open('dumps/llm/best_mtm_pncg.json') as f:
    mtm = json.load(f)

with open('dumps/llm/best_iw_mtm_pncg.json') as f:
    iw = json.load(f)

plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

colors = {
    'baseline': '#3366CC',
    'mtm': '#FF9900',
    'iw': '#33AA33'
}

def plot_method(jwn, label=None, color=None):
    wallclock = np.mean([d['wallclock'] for d in jwn])
    energies = list(zip(*[d['energies'] for d in jwn]))
    means = [np.mean(d) for d in energies]
    lower = [np.percentile(d, q=[5])[0] for d in energies]
    upper = [np.percentile(d, q=[95])[0] for d in energies]

    cross = next((i for i, e in enumerate(means) if e <= 175), 5000)
    cross_time = (cross / 5000) * wallclock

    xs = np.arange(5000)
    plt.plot(xs, means, label=label, color=color, linewidth=2)
    plt.fill_between(xs, lower, upper, alpha=0.2, color=color)

    plt.axvline(cross, color=color, linestyle='--', alpha=0.7)

    text_y = 240 if label == "Importance-Weighted" else (260 if label == "Multiple-Try" else 280)
    plt.annotate(
        f"{label}: ({cross_time:.0f} sec)",
        xy=(cross, 175),
        xytext=(cross+100, text_y),
        color=color,
        fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=color, alpha=0.7)
    )

    return cross, cross_time

baseline_cross, baseline_time = plot_method(baseline, label="Baseline", color=colors['baseline'])
mtm_cross, mtm_time = plot_method(mtm, label="Multiple-Try", color=colors['mtm'])
iw_cross, iw_time = plot_method(iw, label="Importance-Weighted", color=colors['iw'])

plt.axhline(175, color='#777777', linestyle='-', alpha=0.8)

plt.ylabel('Energy $-\\log p(x)$', fontsize=14)
plt.xlabel('Step', fontsize=14)
plt.xlim(0, 5000)
plt.ylim(100, 300)
plt.grid(True, alpha=0.5)
plt.legend(loc='lower right', framealpha=0.8)
plt.tight_layout()

# plt.show()
plt.savefig('figures/llm_comp.png', dpi=300)

# %%
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def parse_data(file_path):
    df = pd.read_csv(file_path)
    return df

for pref in ['iw', 'mtm']:
    font = {'family' : 'normal', 'size': 22}
    matplotlib.rc('font', **font)

    df = parse_data(f'dumps/llm/{pref}_sweep.csv')

    sns.set_theme(style='whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))

    x1 = np.log10(df['alpha'])
    mask1 = ~np.isnan(x1)
    x1_clean = x1[mask1]
    y1_clean = df['ema_energy'][mask1]
    slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(x1_clean, y1_clean)

    ax1.scatter(df['alpha'], df['ema_energy'], alpha=0.5)
    ax1.set_xscale('log')
    ax1.grid(True, alpha=0.5)

    x1_line = np.logspace(np.log10(df['alpha'].min()), np.log10(df['alpha'].max()), 1000)
    y1_line = slope1 * np.log10(x1_line) + intercept1
    ax1.plot(x1_line, y1_line, 'r-')
    ax1.set_xlabel('Step Size')
    ax1.set_ylabel('Energy')

    x2 = np.log10(df['num_samples'])
    mask2 = ~np.isnan(x2)
    x2_clean = x2[mask2]
    y2_clean = df['ema_energy'][mask2]
    slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(x2_clean, y2_clean)

    ax2.scatter(df['num_samples'], df['ema_energy'], alpha=0.5)
    ax2.set_xscale('log')
    ax2.grid(True, alpha=0.5)

    x2_line = np.logspace(np.log10(df['num_samples'].min()), np.log10(df['num_samples'].max()), 1000)
    y2_line = slope2 * np.log10(x2_line) + intercept2
    ax2.plot(x2_line, y2_line, 'r-')
    ax2.set_xlabel('Batch Size')
    ax2.set_ylabel('Energy')

    ax1.text(0.05, 0.85, f'$R^2 = {r_value1**2:.3f}$', transform=ax1.transAxes,
             bbox=dict(facecolor='white', alpha=0.5))

    ax2.text(0.05, 0.85, f'$R^2 = {r_value2**2:.3f}$', transform=ax2.transAxes,
             bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout()
    plt.savefig(f'figures/{pref}_llm_hparams.png', dpi=300)

# %%
import pandas as pd, seaborn as sns, matplotlib.pyplot as plt

df = pd.DataFrame({
    1: [6.71, 6.59, 8.44, 15.98],
    2: [6.82, 7.76, 14.78, 31.64],
    4: [9.80, 14.34, 29.96, 59.35],
    8: [14.74, 29.06, 56.53, 119.09],
    16: [29.20, 54.96, 113.77, 225.23],
    32: [54.35, 111.57, 215.76, 443.83],
    64: [109.69, 210.57, 425.77, 878.79]
}, index=[128, 256, 512, 1024])
df.index.name = 'Sequence Length'
df.columns.name = 'Batch Size'

sns.set_theme(style='whitegrid')
sns.lineplot(
    data=df.reset_index().melt('Sequence Length', var_name='Batch Size', value_name='Time (ms)'),
    x='Batch Size', y='Time (ms)', hue='Sequence Length', marker='o'
)
plt.tight_layout()
plt.savefig('figures/perf_scaling.png', dpi=300)

# %%
import json
import numpy as np

with open('dumps/llm/best_pncg.json') as f:
    baseline = json.load(f)
    baseline_final_energy = np.array([d['energies'][-1] for d in baseline])
    baseline_wallclock = np.array([d['wallclock'] for d in baseline])

with open('dumps/llm/best_mtm_pncg.json') as f:
    mtm = json.load(f)
    mtm_final_energy = np.array([d['energies'][-1] for d in mtm])
    mtm_wallclock = np.array([d['wallclock'] for d in mtm])

with open('dumps/llm/best_iw_mtm_pncg.json') as f:
    iw = json.load(f)
    iw_final_energy = np.array([d['energies'][-1] for d in iw])
    iw_wallclock = np.array([d['wallclock'] for d in iw])

def bootstrap(data):
    return np.percentile([np.mean(np.random.choice(data, size=len(data), replace=True)) for _ in range(1000)], [2.5, 97.5])

print(np.mean(baseline_final_energy), bootstrap(baseline_final_energy))
print(np.mean(mtm_final_energy), bootstrap(mtm_final_energy))
print(np.mean(iw_final_energy), bootstrap(iw_final_energy))
print('###')
print(np.mean(baseline_wallclock), bootstrap(baseline_wallclock))
print(np.mean(mtm_wallclock), bootstrap(mtm_wallclock))
print(np.mean(iw_wallclock), bootstrap(iw_wallclock))
