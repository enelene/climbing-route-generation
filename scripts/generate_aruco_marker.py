"""Generate a printable ArUco marker used as the metric reference on the climbing wall.

The marker lets the geometry module (Phase 1) convert pixel distances in a wall
photo to real centimeters via planar homography: we know the marker's real
printed side length, so any other distance in the same wall plane can be scaled
by pixels-per-cm measured at the marker.

Usage:
    python scripts/generate_aruco_marker.py
    python scripts/generate_aruco_marker.py --marker-id 1 --side-mm 150

Then:
    1. Print marker_<id>.png at 100% scale ("fit to page" OFF / "actual size" ON).
    2. Measure the printed square with a ruler. If it doesn't match --side-mm,
       either reprint at correct scale or record the measured value instead -
       what matters is that marker_<id>_meta.json reflects the REAL printed size.
    3. Tape/stick it flat on the wall, in the same plane as the holds you will
       photograph, before taking wall photos (see data/README.md).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "aruco_marker"


def generate_marker(marker_id: int, dictionary_name: str, side_px: int, side_mm: float) -> Path:
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dictionary_name))
    marker_img = cv2.aruco.generateImageMarker(dictionary, marker_id, side_px)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUTPUT_DIR / f"marker_{marker_id}.png"
    cv2.imwrite(str(png_path), marker_img)

    meta = {
        "marker_id": marker_id,
        "dictionary": dictionary_name,
        "side_px_in_file": side_px,
        "intended_side_mm": side_mm,
        "note": (
            "After printing, measure the actual printed side in mm and update "
            "'measured_side_mm' below before using this marker for homography."
        ),
        "measured_side_mm": None,
    }
    meta_path = OUTPUT_DIR / f"marker_{marker_id}_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return png_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--marker-id", type=int, default=0)
    parser.add_argument(
        "--dictionary",
        type=str,
        default="DICT_4X4_50",
        help="Any cv2.aruco predefined dictionary name, e.g. DICT_4X4_50, DICT_5X5_100",
    )
    parser.add_argument("--side-px", type=int, default=600, help="Marker resolution in the PNG")
    parser.add_argument(
        "--side-mm", type=float, default=150.0, help="Intended printed side length in mm"
    )
    args = parser.parse_args()

    path = generate_marker(args.marker_id, args.dictionary, args.side_px, args.side_mm)
    print(f"Marker written to: {path}")
    print(f"Metadata written to: {path.with_name(path.stem + '_meta.json')}")
    print("Remember to print at 100% / actual size, then measure and fill in measured_side_mm.")


if __name__ == "__main__":
    main()
