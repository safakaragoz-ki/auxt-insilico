#!/usr/bin/env python3
"""Compare ligand-free (apo) and ligand-bound (holo) AuxT models.

For every holo model in models/holo_rfaa/ this script
  1. superposes it on the matching apo model with PyMOL `align`
     (all atoms, default 5 outlier-rejection cycles) - this is the calculation
     behind the RMSD values and aligned-atom counts reported in the manuscript;
  2. additionally reports plain C-alpha RMSDs (no outlier rejection), for the
     whole chain(s) and for the transporter core without the N-terminal
     extension (residues 88-401), and per chain for the dimers;
  3. lists protein residues with any atom within CUTOFF angstrom of the ligand;
  4. reports mean RFAA pLDDT (B-factor column, 0-1) of core, N-terminal
     extension and ligand.

Residues are numbered as in the 401-aa sequence that was modelled. Subtract 87
to obtain the numbering of the revised 314-aa sequence.

Requires PyMOL (pip install pymol-open-source). Run from the repository root:
    python 02_apo_holo_comparison/apo_holo_analysis.py

The defaults analyse the original models (401-aa sequence, AlphaFold3 apo models).
For the RFAA reruns with the revised 314-aa sequence (see arrhenius/README.md):
    python 02_apo_holo_comparison/apo_holo_analysis.py --rerun models/rfaa_rerun --tag AuxT314
"""
import argparse
import csv
import glob
import os
import sys

from pymol import cmd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APO = {"mono": os.path.join(ROOT, "models/apo_alphafold3/HH103_monomer.pdb"),
       "dimer": os.path.join(ROOT, "models/apo_alphafold3/HH103_dimer.pdb")}
HOLO_DIR = os.path.join(ROOT, "models/holo_rfaa")
OUT_DIR = os.path.join(ROOT, "results")
CHAIN_LEN = 401          # modelled sequence length
TAIL = 87                # N-terminal extension absent from the revised annotation
CORE = f"resi {TAIL + 1}-{CHAIN_LEN}"
CUTOFF = 4.0             # angstrom, ligand-residue contact distance


def mean_b(selection):
    store = {"vals": []}
    cmd.iterate(selection, "vals.append(b)", space=store)
    return sum(store["vals"]) / len(store["vals"]) if store["vals"] else float("nan")


def renumber_second_protomer(obj):
    """RFAA numbers chain B CHAIN_LEN+1..2*CHAIN_LEN; map it back to 1..CHAIN_LEN."""
    store = {"vals": []}
    cmd.iterate(f"{obj} and polymer and chain B and name CA", "vals.append(int(resi))", space=store)
    if store["vals"] and min(store["vals"]) > CHAIN_LEN:
        cmd.alter(f"{obj} and polymer and chain B", f"resi=str(int(resi)-{CHAIN_LEN})")
        cmd.sort(obj)


def main():
    global APO, HOLO_DIR, CHAIN_LEN, TAIL, CORE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rerun", help="directory with RFAA rerun models named <tag>_<mono|dimer>_<apo|ligand>.pdb")
    ap.add_argument("--tag", default="AuxT314", help="sequence tag of the rerun models (AuxT314 or AuxT401)")
    args = ap.parse_args()
    prefix, suffix = "HH103_", ""
    if args.rerun:
        HOLO_DIR = os.path.abspath(args.rerun)
        APO = {s: os.path.join(HOLO_DIR, f"{args.tag}_{s}_apo.pdb") for s in ("mono", "dimer")}
        prefix, suffix = args.tag + "_", "_" + args.tag
        if args.tag == "AuxT314":
            CHAIN_LEN, TAIL = 314, 0
        CORE = f"resi {TAIL + 1}-{CHAIN_LEN}"

    os.makedirs(OUT_DIR, exist_ok=True)
    cmd.feedback("disable", "all", "everything")
    rows, contact_rows = [], []
    for path in sorted(glob.glob(os.path.join(HOLO_DIR, prefix + "*.pdb"))):
        name = os.path.basename(path)[:-4]
        if name.endswith("_apo") or "_tetramer_" in name:
            continue
        state = "mono" if "_mono_" in name else "dimer"
        ligand = name.split("_", 2)[2]
        cmd.reinitialize()
        cmd.feedback("disable", "all", "everything")
        cmd.load(APO[state], "apo")
        cmd.load(path, "holo")

        # 1. calculation used in the manuscript
        rmsd_all, n_all = cmd.align("holo and polymer", "apo")[:2]

        # give the second protomer the same numbering as the first so that
        # residues can be paired between models
        cmd.create("h", "holo")
        renumber_second_protomer("h")
        renumber_second_protomer("apo")

        # 2. plain C-alpha RMSDs
        cmd.create("tmp", "h")
        ca_full = cmd.align("tmp and polymer and name CA", "apo and name CA", cycles=0)[:2]
        cmd.create("tmp", "h")
        ca_core = cmd.align(f"tmp and polymer and name CA and {CORE}",
                            f"apo and name CA and {CORE}", cycles=0)[:2]
        per_chain = {}
        if state == "dimer":
            for ch in "AB":
                cmd.create("tmp", "h")
                per_chain[ch] = cmd.align(
                    f"tmp and chain {ch} and name CA and {CORE}",
                    f"apo and chain {ch} and name CA and {CORE}", cycles=0)[0]

        # 3. ligand contacts
        store = {"res": set()}
        cmd.iterate(f"byres (h and polymer within {CUTOFF} of (h and hetatm))",
                    "res.add((chain, int(resi), resn))", space=store)
        contacts = sorted(store["res"])
        for ch, resi, resn in contacts:
            contact_rows.append({
                "model": name, "chain": ch, "residue": resn,
                "number_in_model": resi,
                "number_314aa": resi - TAIL if resi > TAIL else "N-terminal extension",
                "number_401aa_equivalent": resi + (87 - TAIL)})

        rows.append({
            "model": name, "state": state, "ligand": ligand,
            "pymol_align_all_atom_rmsd": round(rmsd_all, 2),
            "pymol_align_n_atoms": n_all,
            "ca_rmsd_full_length": round(ca_full[0], 2),
            "ca_rmsd_core": round(ca_core[0], 2),
            "ca_pairs_core": ca_core[1],
            "ca_rmsd_core_chainA_alone": round(per_chain["A"], 2) if per_chain else "",
            "ca_rmsd_core_chainB_alone": round(per_chain["B"], 2) if per_chain else "",
            "holo_plddt_core": round(mean_b(f"h and polymer and name CA and {CORE}"), 2),
            "holo_plddt_nterm_extension": round(mean_b(f"h and polymer and name CA and resi 1-{TAIL}"), 2) if TAIL else "",
            "holo_plddt_ligand": round(mean_b("h and hetatm"), 2),
            "ligand_heavy_atoms": cmd.count_atoms("h and hetatm"),
            "n_contact_residues": len(contacts),
        })

    for fname, data in ((f"apo_holo_rmsd{suffix}.csv", rows), (f"ligand_contacts_4A{suffix}.csv", contact_rows)):
        with open(os.path.join(OUT_DIR, fname), "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
        print("wrote", os.path.join("results", fname))
    for r in rows:
        print(f"{r['model']:24s} align(all-atom) {r['pymol_align_all_atom_rmsd']:6.2f} A / "
              f"{r['pymol_align_n_atoms']:5d} atoms   CA core {r['ca_rmsd_core']:6.2f} A")


if __name__ == "__main__":
    sys.exit(main())
