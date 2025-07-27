import fabio
from pathlib import Path
import matplotlib.pyplot as plt
import pyFAI
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "powder_cubic_normal"
CALIB_DIR = "agbh_jun_2024"
OUTPUT_DIR = "plot"
FILE_NAME = "Diamond_normal_SiO2_z126_5_master.h5"

input_path = Path(INPUT_DIR).resolve() / FILE_NAME
calib_path = Path(CALIB_DIR).resolve() / "calib.poni"
mask_path = Path(CALIB_DIR).resolve() / "mask.edf"
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Load data
img = fabio.open(input_path).data
ai = pyFAI.load(str(calib_path))
mask = fabio.open(mask_path).data.astype(bool)
img[mask] = 0

# Perform integrations
q_1d, i_1d = ai.integrate1d(img, 200, unit='q_A^-1', mask=mask, radial_range=[0, 0.025])
i_2d, q_2d, phi_2d = ai.integrate2d(img, 200, 180, unit='q_A^-1', mask=mask, radial_range=[0, 0.025])

# Create figure
fig, axes = plt.subplots(1, 3, figsize=(10, 4))

# Panel 1: Original image
axes[0].imshow(img, cmap='hot', vmin=0, vmax=5000)
axes[0].set_xlim(1200, 2000)
axes[0].set_ylim(2200, 1400)
axes[0].set_title('a) Original image')
axes[0].axis('off')

# Panel 2: 2D integration
axes[1].imshow(i_2d, cmap='hot', vmin=0, vmax=5000, aspect='auto',
             extent=[min(q_2d), max(q_2d), min(phi_2d), max(phi_2d)])
axes[1].set_xlim(0, 0.025)
axes[1].set_ylim(-180, 180)
axes[1].set_xlabel('q [A$^{-1}$]')
axes[1].set_ylabel(r'$\chi$ [deg]')
axes[1].set_title('b) 2D integration')

# Panel 3: 1D integration
axes[2].plot(q_1d, i_1d)
axes[2].set_xlim(0, 0.025)
axes[2].set_ylim(1e1, 1e4)
axes[2].set_yscale('log')
axes[2].set_xlabel('q [A$^{-1}$]')
axes[2].set_ylabel('Intensity [a.u.]')
axes[2].set_title('c) 1D integration')

plt.suptitle(f"Ring width: 0.001 [1/A]")
plt.tight_layout()
plt.savefig(output_path / 'powder.pdf')
plt.close(fig) 