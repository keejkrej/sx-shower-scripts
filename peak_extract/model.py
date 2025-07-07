from __future__ import annotations

"""Model layer for the XRD peak extraction application (MVC pattern).
This module knows NOTHING about Qt widgets or the user-interface. It only
manages domain data and business logic.
"""

import dill
from collections import defaultdict
from pathlib import Path

import fabio
import numpy as np

__all__ = [
    "Peak",
    "ImageSeriesModel",
]


class Peak:
    """Container for a single diffraction peak."""

    #Initialization
    def __init__(self, x: int, y: int, data: np.ndarray):
        self.x = x
        self.y = y
        self.data = data  # raw (size × size) excerpt around the peak centre

    def __iter__(self):  # allows unpacking → x, y = peak
        yield from (self.x, self.y)

    def __repr__(self) -> str:  # pragma: no cover – purely cosmetic
        return f"Peak(I={self.intensity}, (x, y)=({self.x}, {self.y}))"

    #Public Methods
    @property
    def intensity(self) -> int:
        """Maximum intensity value within *data*."""
        return int(np.max(self.data))

    @property
    def coordinate(self) -> tuple[int, int]:
        """Return the absolute image coordinate (x, y) of the peak centre."""
        return self.x, self.y


class ImageSeriesModel:
    """Business-logic class working with the image series & detected peaks."""

    #Initialization
    def __init__(self, file_data: str | Path, file_result: str | Path):
        file_data = Path(file_data)
        file_result = Path(file_result)

        if not file_data.exists():
            raise FileNotFoundError(file_data)

        self._file_data: Path = file_data
        self._file_result: Path = file_result

        # Fabio can open a multi-frame series through the first file name
        self._img_series = fabio.open_series(first_filename=str(self._file_data))

        # Initial state values
        self.frame_first: int = 0
        self.frame_last: int = self._img_series.nframes - 1
        self.frame_current: int = 0
        self.frame_step: int = 20

        # Peak storage – *peaks[frame]* ⇒ list[Peak]
        self.peaks: defaultdict[str, list[Peak]] = defaultdict(list)

    #Public Methods - Frame Navigation
    def set_current_frame(self, idx: int) -> None:
        if not (self.frame_first <= idx <= self.frame_last):
            raise ValueError("Frame index out of bounds")
        self.frame_current = idx

    def next_frame(self) -> None:
        self.frame_current = min(self.frame_current + self.frame_step, self.frame_last)

    def prev_frame(self) -> None:
        self.frame_current = max(self.frame_current - self.frame_step, self.frame_first)

    #Public Methods - Image Processing
    def current_image(self) -> np.ndarray:
        """Return a *sanitised* image for *frame_current* as ``np.ndarray``."""
        img = self._img_series.get_frame(self.frame_current).data.astype(np.int32)
        # Basic clean-up (domain-specific)
        img = img.copy()
        img[img > 10000] = 0
        img[img < 0] = 0
        return img

    def extract_peak(self, x: int, y: int, size: int = 9) -> np.ndarray:
        """Return a *size × size* excerpt around *(x, y)* from *current_image*."""
        if size % 2 == 0 or size <= 0:
            raise ValueError("`size` must be an odd positive number")

        img = self.current_image()
        half = size // 2

        # Define desired region bounds
        i_min, i_max = y - half, y + half + 1
        j_min, j_max = x - half, x + half + 1

        # Constrain to image bounds
        img_i_min, img_i_max = max(0, i_min), min(img.shape[0], i_max)
        img_j_min, img_j_max = max(0, j_min), min(img.shape[1], j_max)

        # Create a zero-initialised patch and copy intersection area in
        patch = np.zeros((size, size), dtype=img.dtype)
        i_offset, j_offset = img_i_min - i_min, img_j_min - j_min
        patch[i_offset : i_offset + (img_i_max - img_i_min), j_offset : j_offset + (img_j_max - img_j_min)] = img[
            img_i_min:img_i_max, img_j_min:img_j_max
        ]
        return patch

    #Public Methods - Peak Handling
    def add_peak(self, x: int, y: int, size: int = 9) -> Peak:
        patch = self.extract_peak(x, y, size)
        peak = Peak(x, y, patch)
        self.peaks[str(self.frame_current)].append(peak)
        return peak

    def undo_peak(self) -> None:
        peaks_of_frame = self.peaks[str(self.frame_current)]
        if peaks_of_frame:
            peaks_of_frame.pop()

    #Public Methods - Persistence
    def save_peaks(self) -> None:
        """Dump *peaks* to the *file_result* path using ``dill``."""
        self._file_result.parent.mkdir(parents=True, exist_ok=True)
        with self._file_result.open("wb") as f:
            dill.dump(self.peaks, f)

    #Public Methods - Convenience helpers
    def total_peak_count(self) -> int:
        return sum(map(len, self.peaks.values()))

    def peaks_for_current_frame(self) -> list[Peak]:
        return self.peaks[str(self.frame_current)]