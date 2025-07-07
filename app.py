from pathlib import Path

from peak_extract.controller import run_app

# Constants
DATA_ROOT = Path("/project/ag-nickel/Strahlzeiten/DESY_P62_June_2025/raw/")
EXPERIMENT = "X3_shower1"
FOLDER_DATA = DATA_ROOT / EXPERIMENT
FILE_DATA = FOLDER_DATA / f"{EXPERIMENT}_00001_master.h5"
SAVE_ROOT = Path("/home/t/Tianyi.Cao/scratch/shower/")
FOLDER_RESULT = SAVE_ROOT / EXPERIMENT
FILE_RESULT = FOLDER_RESULT / f"peaks_{EXPERIMENT}.dill"

if __name__ == "__main__":
    run_app(FILE_DATA, FILE_RESULT) 