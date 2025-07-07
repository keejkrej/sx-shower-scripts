from pathlib import Path
import argparse

from extract_peak.controller import run_app

# Constants
DATA_ROOT = Path("/project/ag-nickel/Strahlzeiten/DESY_P62_June_2025/raw/")
EXPERIMENT = "X3_shower1"
FOLDER_DATA = DATA_ROOT / EXPERIMENT / "saxs"
FILE_DATA = FOLDER_DATA / f"{EXPERIMENT}_00001_master.h5"
SAVE_ROOT = Path("/home/t/Tianyi.Cao/scratch/shower/")
FOLDER_RESULT = SAVE_ROOT / EXPERIMENT
FILE_RESULT = FOLDER_RESULT / f"peaks_{EXPERIMENT}.dill"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the peak extraction app with visualization parameters.")
    parser.add_argument("--xrange", nargs=2, type=int, default=[1400, 1700], help="X-axis range for display.")
    parser.add_argument("--yrange", nargs=2, type=int, default=[2100, 1800], help="Y-axis range for display.")
    parser.add_argument("--vmin", type=int, default=0, help="Minimum display intensity.")
    parser.add_argument("--vmax", type=int, default=500, help="Maximum display intensity.")
    args = parser.parse_args()
    run_app(FILE_DATA, FILE_RESULT, args.xrange, args.yrange, args.vmin, args.vmax) 