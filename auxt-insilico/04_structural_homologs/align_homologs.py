#!/usr/bin/env python3
"""Pairwise structural alignment of AuxT with Foldseek hits from the AlphaFold DB.

The AuxT reference is the AlphaFold3 monomer model with the N-terminal
extension removed (residues 88-401 of the modelled 401-aa sequence, i.e. the
revised 314-aa protein, renumbered 1-314). Each homolog is superposed on it with
PyMOL `align` (all atoms, default 5 outlier-rejection cycles); the RMSD and the
number of aligned atoms after refinement are written to a table, together with
a C-alpha-only value. One PNG and one PyMOL session are saved per homolog.

Homolog models are downloaded from the AlphaFold Protein Structure Database by
UniProt accession, or read from --local-dir if a file containing the accession
in its name is found there.

Examples (run from the repository root):
    python 04_structural_homologs/align_homologs.py
    python 04_structural_homologs/align_homologs.py --ids Q9HTA4 --local-dir models/homologs_2024
    python 04_structural_homologs/align_homologs.py --reference my_auxt_model.pdb --keep-reference-as-is

Requires PyMOL (pip install pymol-open-source).
"""
import argparse
import csv
import glob
import json
import os
import urllib.request

from pymol import cmd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Top Foldseek hits against AFDB with the revised (314-aa) AuxT, November 2026
DEFAULT_IDS = {
    "A0A0H3GMW9": "Klebsiella pneumoniae HS11286, auxin efflux carrier",
    "Q9HTA4": "Pseudomonas aeruginosa PAO1, AEC family transporter",
    "A0A0R0ILJ6": "Glycine max, auxin efflux carrier component",
}


def fetch_afdb(acc, dest_dir):
    """Download the AFDB model for a UniProt accession; return the local path."""
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"AF-{acc}.pdb")
    if os.path.exists(dest):
        return dest
    urls = []
    try:
        with urllib.request.urlopen(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}", timeout=60) as r:
            urls.append(json.load(r)[0]["pdbUrl"])
    except Exception as exc:  # fall back to the conventional file names
        print(f"  AFDB API lookup failed for {acc} ({exc}); trying direct file names")
    urls += [f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v{v}.pdb" for v in (6, 5, 4)]
    for url in urls:
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  downloaded {url}")
            return dest
        except Exception:
            continue
    raise SystemExit(f"Could not download an AlphaFold DB model for {acc}. "
                     f"Download it manually and pass --local-dir.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reference", default=os.path.join(ROOT, "models/apo_alphafold3/HH103_monomer.pdb"))
    ap.add_argument("--core", default="88-401",
                    help="residue range of the reference to keep (default: 88-401, removes the N-terminal extension)")
    ap.add_argument("--keep-reference-as-is", action="store_true",
                    help="use the reference file unchanged (e.g. a model predicted from the 314-aa sequence)")
    ap.add_argument("--ids", nargs="+", default=list(DEFAULT_IDS), help="UniProt accessions of the homologs")
    ap.add_argument("--local-dir", help="directory with already downloaded homolog PDB files")
    ap.add_argument("--out", default=os.path.join(ROOT, "results/structural_homologs"))
    ap.add_argument("--no-images", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    cmd.feedback("disable", "all", "everything")

    # reference without the N-terminal extension, renumbered from 1
    cmd.load(args.reference, "ref_full")
    if args.keep_reference_as_is:
        cmd.create("AuxT", "ref_full and polymer and chain A")
    else:
        first = int(args.core.split("-")[0])
        cmd.create("AuxT", f"ref_full and polymer and chain A and resi {args.core}")
        cmd.alter("AuxT", f"resi=str(int(resi)-{first - 1})")
        cmd.sort("AuxT")
    cmd.delete("ref_full")
    ref_out = os.path.join(args.out, "AuxT_notail_reference.pdb")
    cmd.save(ref_out, "AuxT")
    n_ref = cmd.count_atoms("AuxT and name CA")
    print(f"reference: {n_ref} residues -> {ref_out}")

    rows = []
    for acc in args.ids:
        path = None
        if args.local_dir:
            hits = glob.glob(os.path.join(args.local_dir, f"*{acc}*.pdb"))
            path = hits[0] if hits else None
        if path is None:
            path = fetch_afdb(acc, os.path.join(args.out, "afdb_models"))
        cmd.load(path, acc)
        n_res = cmd.count_atoms(f"{acc} and name CA")

        # C-alpha-only superposition on a copy (does not move the displayed object)
        cmd.create("tmp", acc)
        ca = cmd.align("tmp and name CA", "AuxT and name CA")
        cmd.delete("tmp")
        # all-atom superposition, as in the manuscript; `acc` stays superposed
        aa = cmd.align(acc, "AuxT")

        rows.append({
            "uniprot": acc, "description": DEFAULT_IDS.get(acc, ""),
            "homolog_residues": n_res, "auxt_residues": n_ref,
            "rmsd_all_atom_A": round(aa[0], 2), "aligned_atoms": aa[1],
            "rmsd_before_refinement_A": round(aa[3], 2), "atoms_before_refinement": aa[4],
            "rmsd_calpha_A": round(ca[0], 2), "aligned_calpha": ca[1],
        })
        print(f"{acc}: RMSD {aa[0]:.2f} A over {aa[1]} atoms "
              f"(C-alpha only: {ca[0]:.2f} A over {ca[1]} residues)")

        cmd.hide("everything")
        cmd.show("cartoon", f"AuxT or {acc}")
        cmd.color("cyan", "AuxT")
        cmd.color("orange", acc)
        cmd.bg_color("white")
        cmd.set("cartoon_transparency", 0.2)
        cmd.set("cartoon_fancy_helices", 1)
        cmd.set("ray_shadows", 0)
        cmd.set("ray_opaque_background", 0)
        cmd.set("antialias", 2)
        cmd.orient("AuxT")
        cmd.save(os.path.join(args.out, f"AuxT_vs_{acc}.pse"))
        if not args.no_images:
            cmd.png(os.path.join(args.out, f"AuxT_vs_{acc}.png"), width=2400, height=2400, dpi=300, ray=1)
        cmd.delete(acc)

    table = os.path.join(args.out, "structural_alignment_summary.csv")
    with open(table, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("wrote", table)


if __name__ == "__main__":
    main()
