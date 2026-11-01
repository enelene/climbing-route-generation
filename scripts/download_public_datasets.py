"""Helper for pulling public climbing-hold datasets into data/external/.

This project cannot bundle credentials, so this script does NOT auto-download
anything by default - it prints exactly what to go get and where to put it,
and does the mechanical part (unzip/move) once you've downloaded the archive.
See docs/literature_review.md for *which* datasets to actually use and why.

Setup (one-time):
    1. Roboflow: create a free account at https://roboflow.com, get an API key
       from your account settings, then:
           pip install roboflow
           export ROBOFLOW_API_KEY=xxxx   (or set it in a .env file, gitignored)
    2. Kaggle: create an account at https://kaggle.com, go to Account ->
       Create New API Token, which downloads kaggle.json. Put it at
       ~/.kaggle/kaggle.json (chmod 600), then: pip install kaggle

Usage:
    python scripts/download_public_datasets.py --list
    python scripts/download_public_datasets.py --roboflow-project <workspace>/<project> --version 1
    python scripts/download_public_datasets.py --kaggle-dataset <owner>/<dataset-slug>
"""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

EXTERNAL_DIR = Path(__file__).resolve().parent.parent / "data" / "external"

# Candidate datasets worth checking (verify current URLs/availability yourself -
# Roboflow Universe and Kaggle listings change). Fill in / prune this list once
# the literature & dataset review (docs/literature_review.md) is done.
KNOWN_CANDIDATES = [
    (
        "Roboflow Universe search",
        "https://universe.roboflow.com/search?q=climbing%20holds",
        "Search Roboflow Universe directly; several public 'climbing hold detection' "
        "projects exist with bounding boxes for holds/volumes. Pick one with decent "
        "image count and license that allows reuse (check each project's license tab).",
    ),
    (
        "Kaggle search",
        "https://www.kaggle.com/search?q=climbing+hold",
        "Search Kaggle for climbing hold / bouldering wall datasets. Quality and size "
        "vary a lot - inspect sample images before committing to one.",
    ),
]


def list_candidates() -> None:
    print("Known places to look (verify availability/license yourself):\n")
    for name, url, note in KNOWN_CANDIDATES:
        print(f"- {name}\n    {url}\n    {note}\n")


def download_roboflow(project_slug: str, version: int) -> None:
    try:
        from roboflow import Roboflow
    except ImportError as e:
        raise SystemExit("pip install roboflow first") from e

    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        raise SystemExit("Set ROBOFLOW_API_KEY in your environment first")

    workspace, project = project_slug.split("/")
    rf = Roboflow(api_key=api_key)
    ws = rf.workspace(workspace)
    proj = ws.project(project)
    dataset = proj.version(version).download("yolov8", location=str(EXTERNAL_DIR / project))
    print(f"Downloaded to: {dataset.location}")


def download_kaggle(dataset_slug: str) -> None:
    try:
        import kaggle
    except ImportError as e:
        raise SystemExit("pip install kaggle first (and set up ~/.kaggle/kaggle.json)") from e

    target = EXTERNAL_DIR / dataset_slug.split("/")[-1]
    target.mkdir(parents=True, exist_ok=True)
    kaggle.api.dataset_download_files(dataset_slug, path=str(target), unzip=False)

    zips = list(target.glob("*.zip"))
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            zf.extractall(target)
        z.unlink()
    print(f"Downloaded and extracted to: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--list", action="store_true", help="List known dataset sources")
    parser.add_argument("--roboflow-project", type=str, help="<workspace>/<project>")
    parser.add_argument("--version", type=int, default=1, help="Roboflow dataset version")
    parser.add_argument("--kaggle-dataset", type=str, help="<owner>/<dataset-slug>")
    args = parser.parse_args()

    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    if args.list or not (args.roboflow_project or args.kaggle_dataset):
        list_candidates()
        return

    if args.roboflow_project:
        download_roboflow(args.roboflow_project, args.version)

    if args.kaggle_dataset:
        download_kaggle(args.kaggle_dataset)


if __name__ == "__main__":
    main()
