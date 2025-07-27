import sys
sys.path.append("/Users/jack/workspace/own/sx-shower-scripts/extract_peak")

import numpy as np
import dill
import matplotlib.pyplot as plt
import pyFAI
from pathlib import Path
from itertools import chain
from utils.rot import det2q
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "shower_cubic_normal_5"
CALIB_DIR = "agbh_jun_2024"
OUTPUT_DIR = "plot"
FILE_NAME = "peaks_ring_1.dill"

input_path = Path(INPUT_DIR).resolve() / FILE_NAME
calib_path = Path(CALIB_DIR).resolve() / "calib.poni"
mask_path = Path(CALIB_DIR).resolve() / "mask.edf"
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Load data
with open(input_path, "rb") as f:
    peaks = dill.load(f)

peaks_flattened = list(chain.from_iterable(peaks.values()))
peaks_coordinate = list(map(lambda peak: peak.coordinate, peaks_flattened))
ai = pyFAI.load(str(calib_path))

def plot_peaks(ax, point_1, point_2, color, correct):
    """Convert detector coordinates to q-space and plot"""
    q1_1, q2_1, _ = det2q((point_1[1], point_1[0], 0), ai)
    q1_2, q2_2, _ = det2q((point_2[1], point_2[0], 0), ai)
    
    if correct:
        q1_avg, q2_avg = (q1_1 + q1_2)/2, (q2_1 + q2_2)/2
        q1_1 -= q1_avg
        q1_2 -= q1_avg
        q2_1 -= q2_avg
        q2_2 -= q2_avg
    
    ax.plot([q1_1, q1_2], [q2_1, q2_2], 'o-', color=color)
    ax.plot((q1_1 + q1_2)/2, (q2_1 + q2_2)/2, 'o', color=color)
    
    return np.sqrt(q1_1**2 + q2_1**2), np.sqrt(q1_2**2 + q2_2**2)

# Plotting colors
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf', '#000000', '#ffffff'
]

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Plot uncorrected peaks
q_values = []
for i in range(0, len(peaks_coordinate), 2):
    point_1 = peaks_coordinate[i]
    point_2 = peaks_coordinate[i+1]
    q1, q2 = plot_peaks(axes[0], point_1, point_2, colors[(i//2) % len(colors)], correct=False)
    plot_peaks(axes[1], point_1, point_2, colors[(i//2) % len(colors)], correct=False)
    q_values.extend([q1, q2])

axes[0].set_xlabel(r'q$_{\mathrm{x}}$ [A$^{-1}$]')
axes[0].set_ylabel(r'q$_{\mathrm{y}}$ [A$^{-1}$]')
axes[1].set_xlabel(r'q$_{\mathrm{x}}$ [A$^{-1}$]')
axes[1].set_ylabel(r'q$_{\mathrm{y}}$ [A$^{-1}$]')
axes[0].set_xlim(-0.01, 0.01)
axes[0].set_ylim(-0.01, 0.01)
axes[1].set_xlim(-0.001, 0.001)
axes[1].set_ylim(-0.001, 0.001)
axes[0].set_aspect('equal')
axes[1].set_aspect('equal')
axes[0].set_xticks([-0.01, -0.005, 0, 0.005, 0.01])
axes[0].set_yticks([-0.01, -0.005, 0, 0.005, 0.01])
axes[1].set_xticks([-0.001, -0.0005, 0, 0.0005, 0.001])
axes[1].set_yticks([-0.001, -0.0005, 0, 0.0005, 0.001])

# Titles
axes[0].set_title('a) q-space')
axes[1].set_title('b) q-space, zoomed')
plt.suptitle(f"Uncorrected, ring width: {0.0006:.1e} [1/A]")

plt.tight_layout()
plt.savefig(output_path / 'peaks_uncorrected.pdf')
plt.close(fig)

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Plot corrected peaks
q_values = []
for i in range(0, len(peaks_coordinate), 2):
    point_1 = peaks_coordinate[i]
    point_2 = peaks_coordinate[i+1]
    q1, q2 = plot_peaks(axes[0], point_1, point_2, colors[(i//2) % len(colors)], correct=True)
    plot_peaks(axes[1], point_1, point_2, colors[(i//2) % len(colors)], correct=True)
    q_values.extend([q1, q2])

axes[0].set_xlabel(r'q$_{\mathrm{x}}$ [A$^{-1}$]')
axes[0].set_ylabel(r'q$_{\mathrm{y}}$ [A$^{-1}$]')
axes[1].set_xlabel(r'q$_{\mathrm{x}}$ [A$^{-1}$]')
axes[1].set_ylabel(r'q$_{\mathrm{y}}$ [A$^{-1}$]')
axes[0].set_xlim(-0.01, 0.01)
axes[0].set_ylim(-0.01, 0.01)
axes[1].set_xlim(-0.001, 0.001)
axes[1].set_ylim(-0.001, 0.001)
axes[0].set_aspect('equal')
axes[1].set_aspect('equal')
axes[0].set_xticks([-0.01, -0.005, 0, 0.005, 0.01])
axes[0].set_yticks([-0.01, -0.005, 0, 0.005, 0.01])
axes[1].set_xticks([-0.001, -0.0005, 0, 0.0005, 0.001])
axes[1].set_yticks([-0.001, -0.0005, 0, 0.0005, 0.001])

# Titles
axes[0].set_title('a) q-space')
axes[1].set_title('b) q-space, zoomed')
plt.suptitle(f"Corrected, ring width: {0.0001:.1e} [1/A]")

plt.tight_layout()
plt.savefig(output_path / 'peaks_corrected.pdf')
plt.close(fig)



