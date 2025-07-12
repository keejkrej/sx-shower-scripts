from pathlib import Path

from controller import run_app

# Constants
INPUT_DIR = "shower_cubic_normal_5"
CALIB_DIR = "agbh_jun_2024"
OUTPUT_DIR = "shower_cubic_normal_5"
FILE_NAME = "Diamond_shower_normal_SiO2_5_master.h5"

input_path = Path(INPUT_DIR).resolve() / FILE_NAME
calib_path = Path(CALIB_DIR).resolve() / "calib.poni"
mask_path = Path(CALIB_DIR).resolve() / "mask.edf"
output_path = Path(OUTPUT_DIR).resolve() / "peaks.dill"
output_path.parent.mkdir(parents=True, exist_ok=True)

run_app(input_path, output_path, [1400, 1800], [2000, 1600], 0, 500)