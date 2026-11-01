"""Smoke test: confirms the dev environment (venv, deps, package layout) works end to end."""

import cv2
import networkx as nx
import numpy as np


def test_opencv_aruco_available():
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    assert aruco_dict is not None


def test_networkx_graph_roundtrip():
    g = nx.Graph()
    g.add_edge("hold_1", "hold_2", weight=1.0)
    assert g.number_of_nodes() == 2
    assert g.number_of_edges() == 1


def test_numpy_basic():
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6


def test_package_importable():
    import climbing_route_gen

    assert climbing_route_gen.__version__
