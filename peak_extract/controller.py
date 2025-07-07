from __future__ import annotations

"""Controller layer for the XRD peak extraction application (MVC pattern).
The controller wires *Model* ↔ *View*: it reacts to signals from the *View*,
updates the *Model*, and refreshes the *View* accordingly.
"""

import sys
from pathlib import Path
from typing import Tuple

from PyQt5.QtWidgets import QApplication

from .model import ImageSeriesModel
from .view import Viewer

__all__ = ["ViewerController", "run_app"]


class ViewerController:  # noqa: D401 – orchestrator class
    """Glue-class connecting *ImageSeriesModel* and *Viewer*."""

    #Initialization
    def __init__(self, file_data: str | Path, file_result: str | Path):
        # Initialise model & view
        self._model = ImageSeriesModel(file_data, file_result)
        self._view = Viewer(
            frame_first=self._model.frame_first,
            frame_last=self._model.frame_last,
            frame_current=self._model.frame_current,
            vmin=self._model.vmin,
            vmax=self._model.vmax,
            xrange=self._model.xrange,
            yrange=self._model.yrange,
        )

        # Connect signals
        self._view.prev_requested.connect(self._on_prev)
        self._view.next_requested.connect(self._on_next)
        self._view.frame_changed.connect(self._on_frame_changed)
        self._view.add_peak_toggled.connect(self._on_add_peak_toggled)
        self._view.undo_requested.connect(self._on_undo)
        self._view.save_requested.connect(self._on_save)
        self._view.canvas_clicked.connect(self._on_canvas_click)

        # Initial render
        self._refresh_view(full=True)

    #Private Methods
    def _on_prev(self):
        self._model.prev_frame()
        self._refresh_view()

    def _on_next(self):
        self._model.next_frame()
        self._refresh_view()

    def _on_frame_changed(self, idx: int):
        self._model.set_current_frame(idx)
        self._refresh_view(full=False)  # no need to redraw slider

    def _on_add_peak_toggled(self, enabled: bool):
        # Nothing to do on the model side. Kept for completeness.
        pass

    def _on_undo(self):
        self._model.undo_peak()
        self._refresh_view()

    def _on_save(self):
        self._model.save_peaks()

    def _on_canvas_click(self, x: int, y: int):
        self._model.add_peak(x, y)
        self._refresh_view()

    #Public Methods
    @property
    def widget(self):
        """Return the underlying *Viewer* widget for showing/embedding."""
        return self._view

    def _refresh_view(self, *, full: bool = True):
        img = self._model.current_image()
        self._view.set_image(img)
        coords: list[Tuple[int, int]] = [p.coordinate() for p in self._model.peaks_for_current_frame()]
        self._view.set_markers(coords)
        self._view.set_info(self._model.frame_current, self._model.total_peak_count())
        if full:
            self._view.set_slider_position(self._model.frame_current)


def run_app(file_data: str | Path, file_result: str | Path):
    app = QApplication.instance() or QApplication(sys.argv)
    ctrl = ViewerController(file_data, file_result)
    ctrl.widget.show()
    sys.exit(app.exec_()) 