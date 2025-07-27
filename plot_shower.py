import os
import numpy as np
import fabio
from pathlib import Path
import matplotlib.pyplot as plt
import pyFAI
from matplotlib.patches import Rectangle
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "shower_cubic_normal_5"
CALIB_DIR = "agbh_jun_2024"
OUTPUT_DIR = "plot"
FILE_NAME = "Diamond_shower_normal_SiO2_5_master.h5"

input_path = Path(INPUT_DIR).resolve() / FILE_NAME
calib_path = Path(CALIB_DIR).resolve() / "calib.poni"
mask_path = Path(CALIB_DIR).resolve() / "mask.edf"
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Load data
img = fabio.open(input_path, frame=500).data

ai = pyFAI.load(str(calib_path))
mask = fabio.open(mask_path).data.astype(bool)
img[mask] = 0

# Perform integrations
i_2d, q_2d, phi_2d = ai.integrate2d(img, 200, 180, unit='q_A^-1', mask=mask, radial_range=[0, 0.025])

# Create figure
fig, axes = plt.subplots(1, 3, figsize=(10, 4))

# Panel 1: Original image
axes[0].imshow(img, cmap='hot', vmin=0, vmax=500)
axes[0].set_xlim(1400, 1800)
axes[0].set_ylim(2000, 1600)
axes[0].set_title('a) Original image')
axes[0].axis('off')

# Panel 2: Transformed coordinates with zoom rectangle
axes[1].imshow(i_2d, cmap='hot', vmin=0, vmax=500, aspect='auto', 
            extent=[min(q_2d), max(q_2d), min(phi_2d), max(phi_2d)])
axes[1].set_xlim(0, 0.02)
axes[1].set_ylim(-180, 180)
axes[1].set_xlabel('q [A$^{-1}$]')
axes[1].set_ylabel(r'$\chi$ [deg]')
axes[1].set_title('b) 2D integration')

# Add zoom rectangle
zoom_area = Rectangle((0.006, -180), 0.002, 360, linewidth=1, edgecolor='white', facecolor='none')
axes[1].add_patch(zoom_area)

# Panel 3: Zoomed peaks with lines
axes[2].imshow(i_2d, cmap='hot', vmin=0, vmax=500, aspect='auto',
            extent=[min(q_2d), max(q_2d), min(phi_2d), max(phi_2d)])
axes[2].set_xlim(0.006, 0.008)
axes[2].set_ylim(-180, 180)
axes[2].set_xlabel('q [A$^{-1}$]')
axes[2].set_ylabel(r'$\chi$ [deg]')
axes[2].set_title('c) 2D integration, zoomed')

# Add peak lines
line_1 = [(0.00636, 0.00705), (-156, 24)]
line_2 = [(0.00659, 0.00671), (-61, 119)]
line_3 = [(0.00659, 0.00671), (-120, 60)]
line_4 = [(0.00670, 0.00660), (-10, 170)]
axes[2].plot(*line_1, color='white', linewidth=1)
axes[2].plot(*line_2, color='white', linewidth=1)
axes[2].plot(*line_3, color='white', linewidth=1)
axes[2].plot(*line_4, color='white', linewidth=1)

plt.suptitle(f"Peak width: 0.0003 [1/A]")
plt.tight_layout()
plt.savefig(output_path / 'shower.pdf')
plt.close(fig)