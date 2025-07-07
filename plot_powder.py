import os
import numpy as np
import fabio
from pathlib import Path
import matplotlib.pyplot as plt
import pyFAI
import argparse

# Constants (aligned with app.py)
DATA_ROOT = Path("/project/ag-nickel/Strahlzeiten/DESY_P62_June_2025/raw/")
EXPERIMENT = "X3_shower1"
FOLDER_DATA = DATA_ROOT / EXPERIMENT / "saxs"
FILE_DATA = FOLDER_DATA / f"{EXPERIMENT}_00001_master.h5"  # Using same file as app.py
SAVE_ROOT = Path("/home/t/Tianyi.Cao/scratch/shower/")
FOLDER_RESULT = SAVE_ROOT / EXPERIMENT

# Parse arguments
parser = argparse.ArgumentParser(description="Plot powder diffraction pattern with 1D and 2D integration.")
parser.add_argument("--xrange", nargs=2, type=int, default=[1350, 1950], help="X-axis range for display.")
parser.add_argument("--yrange", nargs=2, type=int, default=[2850, 2250], help="Y-axis range for display.")
parser.add_argument("--vmin", type=int, default=0, help="Minimum display intensity.")
parser.add_argument("--vmax", type=int, default=5000, help="Maximum display intensity.")
parser.add_argument("--qmax", type=float, default=0.025, help="Maximum q value for plots.")
args = parser.parse_args()

# Load data
img = fabio.open(FILE_DATA).data.astype(np.int32).astype(np.float32)
ai = pyFAI.load(FOLDER_RESULT / "peaks_X3_shower1.dill")  # Using calibration from peaks file
mask = img < 0

# Perform integrations
q_1d, i_1d = ai.integrate1d(img, 5000, unit='q_A^-1', mask=mask)
i_2d, q_2d, phi_2d = ai.integrate2d(img, 5000, 720, unit='q_A^-1', mask=mask)

# Create figure
fig, ax = plt.subplots(1, 3, figsize=(15, 6))
fig.subplots_adjust(left=0.1, right=0.9, top=0.8, bottom=0.1, wspace=0.5)

# Panel 1: Original image
ax[0].imshow(img, cmap='hot', vmin=args.vmin, vmax=args.vmax)
ax[0].set_xlim(*args.xrange)
ax[0].set_ylim(*args.yrange)
ax[0].set_xlabel('x (px)', weight='bold')
ax[0].set_ylabel('y (px)', weight='bold')

# Panel 2: 2D integration
ax[1].imshow(i_2d, cmap='hot', vmin=args.vmin, vmax=args.vmax, aspect='auto',
             extent=[min(q_2d), max(q_2d), min(phi_2d), max(phi_2d)])
ax[1].set_xlim(0, args.qmax)
ax[1].set_ylim(-180, 180)
ax[1].set_xlabel('q (A^-1)', weight='bold')
ax[1].set_ylabel('phi (deg)', weight='bold')

# Panel 3: 1D integration (log scale)
ax[2].plot(q_1d, i_1d, color='black')
ax[2].set_xlim(0, args.qmax)
ax[2].set_ylim(1e1, 1e4)
ax[2].set_yscale('log')
ax[2].set_xlabel('q (A^-1)', weight='bold')
ax[2].set_ylabel('Intensity (a.u.)', weight='bold')

# Titles
ax[0].set_title('ring width:\n14 px = 1050 um', weight='bold')
ax[1].set_title('ring width:\n0.0087 nm^-1 = 2pi / (720 nm)', weight='bold')
fig.suptitle('SAXS of DNA diamond powder', weight='bold', fontsize=16)

plt.savefig(FOLDER_RESULT / 'powder_diffraction.png', dpi=300)
plt.show() 