from __future__ import annotations

"""View layer for the XRD peak extraction application (MVC pattern).
The *Viewer* widget renders the image, handles user interaction (buttons,
mouse clicks, etc.) and exposes *Qt* signals so that a *Controller* can react
appropriately. The widget itself knows NOTHING about how to handle data – it
just forwards events and waits for methods to be called to update its visuals.
"""

from typing import List, Tuple

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt import (
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg", force=True)  # Ensure Qt5 backend is active

__all__ = ["Viewer"]


class Viewer(QWidget):  # noqa: D401 – widget class
    """Qt widget that displays the image series and UI controls."""

    # Signals emitted for the controller to react to
    prev_requested = pyqtSignal()
    next_requested = pyqtSignal()
    frame_changed = pyqtSignal(int)
    add_peak_toggled = pyqtSignal(bool)
    undo_requested = pyqtSignal()
    save_requested = pyqtSignal()
    canvas_clicked = pyqtSignal(int, int)  # x, y coordinates in image space

    #Initialization
    def __init__(
        self,
        frame_first: int,
        frame_last: int,
        frame_current: int,
        vmin: int,
        vmax: int,
        xrange: List[int],
        yrange: List[int],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Store axis limits so that the controller can update them later if
        # desired via *set_axis_limits()*.
        self._xrange = xrange
        self._yrange = yrange

        # Qt layout & widget construction
        self.setWindowTitle("XRD Image Viewer")
        self.setMinimumSize(800, 1000)

        self._root_layout = QVBoxLayout(self)

        # Matplotlib figure & canvas
        self._fig = plt.figure(figsize=(8, 8))
        self._ax = self._fig.add_subplot(111)
        self._im = self._ax.imshow(np.zeros((10, 10)), cmap="hot", vmin=vmin, vmax=vmax)
        self._canvas = FigureCanvas(self._fig)
        self._toolbar = NavigationToolbar(self._canvas, self)

        # Control bar
        self._prev_btn = QPushButton("Previous")
        self._next_btn = QPushButton("Next")
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(frame_first)
        self._slider.setMaximum(frame_last)
        self._slider.setValue(frame_current)

        self._add_peak_btn = QPushButton("Add Peak")
        self._undo_btn = QPushButton("Undo")
        self._save_btn = QPushButton("Save Peaks")

        # Layout the controls neatly
        ctrl_row1 = QHBoxLayout()
        ctrl_row1.addWidget(self._prev_btn)
        ctrl_row1.addWidget(self._next_btn)
        ctrl_row1.addWidget(self._slider)

        ctrl_row2 = QHBoxLayout()
        ctrl_row2.addWidget(self._add_peak_btn)
        ctrl_row2.addWidget(self._undo_btn)
        ctrl_row2.addWidget(self._save_btn)

        ctrl_layout = QVBoxLayout()
        ctrl_layout.addLayout(ctrl_row1)
        ctrl_layout.addLayout(ctrl_row2)

        # Info groupbox
        self._info_group = QGroupBox()
        info_layout = QHBoxLayout(self._info_group)
        self._frame_label = QLabel(f"Frame: {frame_current}")
        self._peaks_label = QLabel("Peaks: 0")
        info_layout.addWidget(self._frame_label)
        info_layout.addWidget(self._peaks_label)

        # Compose into root layout
        self._root_layout.addWidget(self._toolbar)
        self._root_layout.addLayout(ctrl_layout)
        self._root_layout.addWidget(self._canvas)
        self._root_layout.addWidget(self._info_group, alignment=Qt.AlignCenter)

        # Signal wiring (to *self* → forward to public signals)
        self._prev_btn.clicked.connect(self.prev_requested)
        self._next_btn.clicked.connect(self.next_requested)
        self._slider.valueChanged.connect(self.frame_changed)
        self._add_peak_btn.clicked.connect(self._toggle_add_peak)
        self._undo_btn.clicked.connect(self.undo_requested)
        self._save_btn.clicked.connect(self.save_requested)

        # Matplotlib canvas click handling
        self._add_peak_mode = False
        self._canvas.mpl_connect("button_press_event", self._on_canvas_click)

        # Apply initial axis limits
        self._update_axis_limits()

    #Private Methods
    def _toggle_add_peak(self):
        self._add_peak_mode = not self._add_peak_mode
        if self._add_peak_mode:
            self._add_peak_btn.setStyleSheet("background-color: red; color: white;")
        else:
            self._add_peak_btn.setStyleSheet("")
        self.add_peak_toggled.emit(self._add_peak_mode)

    def _on_canvas_click(self, event):
        if (
            event.button
            and event.inaxes == self._ax
            and self._add_peak_mode
            and self._toolbar.mode == ""
        ):
            x, y = int(event.xdata), int(event.ydata)
            self.canvas_clicked.emit(x, y)

    def _update_axis_limits(self):
        self._ax.set_xlim(self._xrange)
        self._ax.set_ylim(self._yrange)
        self._canvas.draw()

    #Public Methods
    def set_image(self, img: np.ndarray) -> None:
        self._im.set_data(img)
        self._im.set_extent((0, img.shape[1], img.shape[0], 0))
        self._canvas.draw()

    def set_markers(self, coordinates: List[Tuple[int, int]]):
        # Remove old markers first
        for artist in getattr(self, "_markers", []):
            artist.remove()
        self._markers = []
        for x, y in coordinates:
            (marker,) = self._ax.plot(x, y, "x", markersize=10, color="white")
            self._markers.append(marker)
        self._canvas.draw()

    def set_info(self, frame_idx: int, peak_count: int) -> None:
        self._frame_label.setText(f"Frame: {frame_idx}")
        self._peaks_label.setText(f"Peaks: {peak_count}")

    def set_slider_position(self, frame_idx: int) -> None:
        self._slider.blockSignals(True)
        self._slider.setValue(frame_idx)
        self._slider.blockSignals(False)

    def set_axis_limits(self, xrange: List[int], yrange: List[int]):
        self._xrange = xrange
        self._yrange = yrange
        self._update_axis_limits()