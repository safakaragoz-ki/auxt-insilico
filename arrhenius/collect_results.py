#!/usr/bin/env python3
"""Collect finished RFAA runs: copy models into the repository and tabulate confidences.

    python arrhenius/collect_results.py <RUN_DIR> [--out models/rfaa_314aa]

Writes <out>/<job>.pdb and results/rfaa_confidence_<tag>.csv with mean pLDDT,
mean PAE, protein PAE and protein-ligand PAE (pae_inter; RFAA's authors treat
pae_inter < 10 as a confident ligand placement). Needs torch (use the RFAA env).
"""
import argparse
import csv
import glob
import os
import shutil

import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--out", default=os.path.join(ROOT, "models/rfaa_rerun"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = []
    for aux in sorted(glob.glob(os.path.join(args.run_dir, "*_aux.pt"))):
        job = os.path.basename(aux)[:-len("_aux.pt")]
        pdb = os.path.join(args.run_dir, job + ".pdb")
        if not os.path.exists(pdb):
            continue
        d = torch.load(aux, map_location="cpu")
        shutil.copy(pdb, args.out)
        fmt = lambda v: "" if v is None or v != v else round(float(v), 3)
        rows.append({"job": job, "mean_plddt": fmt(d.get("mean_plddt")), "mean_pae": fmt(d.get("mean_pae")),
                     "pae_prot": fmt(d.get("pae_prot")), "pae_inter": fmt(d.get("pae_inter"))})
    if not rows:
        raise SystemExit(f"no finished runs in {args.run_dir}")
    table = os.path.join(ROOT, "results", "rfaa_rerun_confidence.csv")
    os.makedirs(os.path.dirname(table), exist_ok=True)
    with open(table, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"copied {len(rows)} models to {args.out}; wrote {table}")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
