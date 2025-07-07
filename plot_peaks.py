import os
import numpy as np
import dill
import matplotlib.pyplot as plt
import pyFAI
import argparse
from pathlib import Path
from itertools import chain
from utils.rot import det2q  # Import from new utils location

# Argument parsing
parser = argparse.ArgumentParser(description="Plot peaks in q-space from .dill file")
parser.add_argument("--dill_path", type=str, required=True, help="Path to .dill file containing peaks")
parser.add_argument("--poni_path", type=str, required=True, help="Path to .poni calibration file")
parser.add_argument("--qmax", type=float, default=0.01, help="Maximum q value for plots")
parser.add_argument("--corrected", action="store_true", help="Apply correction to peak positions")
args = parser.parse_args()

# Load data
with open(args.dill_path, 'rb') as f:
    peaks = dill.load(f)
peaks_flattened = list(chain.from_iterable(peaks.values()))
peaks_coordinate = list(map(lambda peak: peak.get_coordinate(), peaks_flattened))
ai = pyFAI.load(args.poni_path)

# Create figure
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.3)

# Plotting colors
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf', '#000000', '#ffffff'
]

def plot_peaks(ax, point_1, point_2, color):
    """Convert detector coordinates to q-space and plot"""
    q1_1, q2_1, _ = det2q((point_1[1], point_1[0], 0), ai)
    q1_2, q2_2, _ = det2q((point_2[1], point_2[0], 0), ai)
    
    if args.corrected:
        q1_avg, q2_avg = (q1_1 + q1_2)/2, (q2_1 + q2_2)/2
        q1_1 -= q1_avg
        q1_2 -= q1_avg
        q2_1 -= q2_avg
        q2_2 -= q2_avg
    
    ax.plot([q1_1, q1_2], [q2_1, q2_2], 'o-', color=color)
    ax.plot((q1_1 + q1_2)/2, (q2_1 + q2_2)/2, 'o', color=color)
    
    return np.sqrt(q1_1**2 + q2_1**2), np.sqrt(q1_2**2 + q2_2**2)

# Main plotting loop
q_values = []
for i in range(0, len(peaks_coordinate), 2):
    point_1 = peaks_coordinate[i]
    point_2 = peaks_coordinate[i+1]
    q1, q2 = plot_peaks(ax[0], point_1, point_2, colors[(i//2) % len(colors)])
    plot_peaks(ax[1], point_1, point_2, colors[(i//2) % len(colors)])
    q_values.extend([q1, q2])

# Configure axes
for a in ax:
    a.set_aspect('equal')
    a.set_xlabel('q_x [1/A]', weight='bold')
    a.set_ylabel('q_y [1/A]', weight='bold')
    a.grid(True)

ax[0].set_xlim(-args.qmax, args.qmax)
ax[0].set_ylim(-args.qmax, args.qmax)
ax[1].set_xlim(-args.qmax/10, args.qmax/10)
ax[1].set_ylim(-args.qmax/10, args.qmax/10)

# Titles
ax[0].set_title('q-space' + (' (corrected)' if args.corrected else ''), weight='bold')
ax[1].set_title('q-space zoomed' + (' (corrected)' if args.corrected else ''), weight='bold')
fig.suptitle(f'Peak positions in reciprocal space\nRing width: {max(q_values)-min(q_values):.4f} [1/A]', 
             weight='bold', fontsize=16)

plt.savefig(Path(args.dill_path).parent / 'qspace_peaks.png', dpi=300)
plt.show()