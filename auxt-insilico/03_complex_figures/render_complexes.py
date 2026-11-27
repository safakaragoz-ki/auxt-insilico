#!/usr/bin/env python3
"""Render AuxT models (apo or ligand-bound) from four viewing angles with PyMOL.

Protein chains are drawn as cartoons (chain A cyan, B orange, C/D green/salmon),
ligands (HETATM) as gold sticks. Images are ray-traced at 2400 x 2400 px, 300 dpi,
after rotations of 0, 90, 180 and 270 degrees about the y axis.

    python 03_complex_figures/render_complexes.py                      # all models
    python 03_complex_figures/render_complexes.py models/holo_rfaa/HH103_mono_IAA.pdb

Requires PyMOL (pip install pymol-open-source).
"""
import glob
import os
import sys

from pymol import cmd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "figures")
CHAIN_COLORS = {"A": "cyan", "B": "orange", "C": "palegreen", "D": "salmon"}
ANGLES = (0, 90, 180, 270)


def render(pdb_path, size=2400):
    name = os.path.basename(pdb_path)[:-4]
    cmd.reinitialize()
    cmd.feedback("disable", "all", "everything")
    cmd.load(pdb_path, "complex")
    cmd.hide("everything")
    cmd.show("cartoon", "complex and polymer")
    for chain in cmd.get_chains("complex and polymer"):
        cmd.color(CHAIN_COLORS.get(chain, "grey70"), f"complex and polymer and chain {chain}")
    cmd.show("sticks", "complex and hetatm")
    cmd.color("gold", "complex and hetatm")
    cmd.bg_color("white")
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("cartoon_side_chain_helper", 1)
    cmd.set("ray_shadows", 0)
    cmd.set("ray_opaque_background", 0)
    cmd.set("antialias", 2)
    cmd.orient("complex")
    previous = 0
    for angle in ANGLES:
        cmd.turn("y", angle - previous)
        previous = angle
        cmd.png(os.path.join(OUT_DIR, f"{name}_view{angle}.png"), width=size, height=size, dpi=300, ray=1)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = sys.argv[1:] or sorted(
        glob.glob(os.path.join(ROOT, "models/apo_alphafold3/*.pdb")) +
        glob.glob(os.path.join(ROOT, "models/holo_rfaa/*.pdb")))
    for path in paths:
        render(path)
        print("rendered", os.path.basename(path))


if __name__ == "__main__":
    main()
