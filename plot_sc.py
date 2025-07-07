import os
import numpy as np
import fabio
from pathlib import Path
import matplotlib.pyplot as plt
import pyFAI
from matplotlib.patches import Rectangle
import argparse

# Constants (aligned with app.py)
DATA_ROOT = Path("/project/ag-nickel/Strahlzeiten/DESY_P62_June_2025/raw/")
EXPERIMENT = "X3_shower1"
FOLDER_DATA = DATA_ROOT / EXPERIMENT / "saxs"
FILE_DATA = FOLDER_DATA / f"{EXPERIMENT}_00001_master.h5"
SAVE_ROOT = Path("/home/t/Tianyi.Cao/scratch/shower/")
FOLDER_RESULT = SAVE_ROOT / EXPERIMENT
FILE_RESULT = FOLDER_RESULT / f"peaks_{EXPERIMENT}.dill"

# Parse arguments
parser = argparse.ArgumentParser(description="Plot X-ray diffraction image with coordinate transformation and zoom on peak pairs.")
parser.add_argument("--xrange", nargs=2, type=int, default=[1400, 1700], help="X-axis range for display.")
parser.add_argument("--yrange", nargs=2, type=int, default=[2100, 1800], help="Y-axis range for display.")
parser.add_argument("--vmin", type=int, default=0, help="Minimum display intensity.")
parser.add_argument("--vmax", type=int, default=500, help="Maximum display intensity.")
args = parser.parse_args()

# Load data
img_0 = fabio.open(FILE_DATA).data.astype(np.int32).astype(np.float32)
ai = pyFAI.load(FILE_RESULT)  # Assuming calibration is stored in peaks file
mask = img_0 < 0
i_2d, q_2d, phi_2d = ai.integrate2d(img_0, 5000, 720, unit='q_A^-1', mask=mask)

# Plot
fig, ax = plt.subplots(1, 3, figsize=(15, 6))
fig.subplots_adjust(left=0.1, right=0.9, top=0.8, bottom=0.1, wspace=0.5)

# Panel 1: Original image
ax[0].imshow(img_0, cmap='hot', vmin=args.vmin, vmax=args.vmax)
ax[0].set_xlim(*args.xrange)
ax[0].set_ylim(*args.yrange)
ax[0].set_xlabel('x (px)', weight='bold')
ax[0].set_ylabel('y (px)', weight='bold')

# Panel 2: Transformed coordinates with zoom rectangle
ax[1].imshow(i_2d, cmap='hot', vmin=args.vmin, vmax=args.vmax, aspect='auto', 
            extent=[min(q_2d), max(q_2d), min(phi_2d), max(phi_2d)])
ax[1].set_xlim(0, 0.02)
ax[1].set_ylim(-180, 180)
ax[1].set_xlabel('q (A^-1)', weight='bold')
ax[1].set_ylabel('phi (deg)', weight='bold')

# Add zoom rectangle (from original shower_#0.py)
zoom_area = Rectangle((0.006, -60), 0.002, 220, linewidth=1, edgecolor='white', facecolor='none')
ax[1].add_patch(zoom_area)

# Panel 3: Zoomed peaks with lines (from original shower_#0.py)
ax[2].imshow(i_2d, cmap='hot', vmin=args.vmin, vmax=args.vmax, aspect='auto',
            extent=[min(q_2d), max(q_2d), min(phi_2d), max(phi_2d)])
ax[2].set_xlim(0.006, 0.008)
ax[2].set_ylim(-180, 180)
ax[2].set_xlabel('q (A^-1)', weight='bold')
ax[2].set_ylabel('phi (deg)', weight='bold')

# Add peak lines (from original shower_#0.py)
line_vert = [(0.00665, 0.00665), (-40, 140)]
line_tilt = [(0.00650, 0.00684), (-50, 130)]
ax[2].plot(*line_vert, color='white', linewidth=1)
ax[2].plot(*line_tilt, color='white', linewidth=1)

# Titles (from original shower_#0.py)
ax[0].set_title('peak width:\n3 px = 225 um', weight='bold')
ax[1].set_title('peak width:\n0.0022 nm^-1 = 2pi / (2850 nm)', weight='bold')
fig.suptitle(f'SAXS of {EXPERIMENT}', weight='bold', fontsize=16)

plt.savefig(FOLDER_RESULT / 'xray_diffraction.png', dpi=300)
plt.show()