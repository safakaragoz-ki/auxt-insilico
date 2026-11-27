#!/usr/bin/env python3
"""Generate the Hydra configs for the AuxT RFAA reruns.

Writes into CONFIG_DIR:
  base.yaml      copy of rf2aa/config/inference/base.yaml with the Arrhenius paths filled in
  <job>.yaml     one config per job (same layout as RFAA's protein.yaml / protein_sm.yaml /
                 protein_complex_sm.yaml)
  jobs.txt       job names, one per line (index = Slurm array task id, starting at 1)

Job set for each sequence tag (default: the revised 314-aa AuxT, tag "AuxT314"):
  <tag>_mono_apo, <tag>_dimer_apo, <tag>_tetramer_apo
  <tag>_mono_<ligand>, <tag>_dimer_<ligand>   for IAA, 4-Cl-IAA, IBA, PAA
Protein chains are A, B, (C, D); the ligand is the next free chain letter.

Needs only PyYAML. All paths are passed in by `make_configs.sh`, which reads settings.sh.
"""
import argparse
import os
import yaml

LIGANDS = {"IAA": "IAA.sdf", "4-Cl-IAA": "4-Cl-IAA.sdf", "IBA": "IBA.sdf", "PAA": "PAA_2d.sdf"}
STATES = {"mono": 1, "dimer": 2, "tetramer": 4}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rfaa-dir", required=True)
    ap.add_argument("--config-dir", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--template-db", required=True)
    ap.add_argument("--sequence-db", required=True)
    ap.add_argument("--ligand-dir", required=True)
    ap.add_argument("--fasta", action="append", required=True, metavar="TAG=FASTA",
                    help="sequence tag and FASTA file; repeat for more sequences")
    ap.add_argument("--maxcycle", type=int, default=4,
                    help="recycles (RFAA default 4; its README suggests 10 for hard cases)")
    ap.add_argument("--cpus", type=int, default=16)
    ap.add_argument("--mem", type=int, default=64)
    args = ap.parse_args()

    os.makedirs(args.config_dir, exist_ok=True)
    with open(os.path.join(args.rfaa_dir, "rf2aa/config/inference/base.yaml")) as fh:
        base = yaml.safe_load(fh)
    base["output_path"] = args.run_dir
    base["checkpoint_path"] = args.weights
    base["database_params"].update({
        "sequencedb": args.sequence_db, "hhdb": args.template_db,
        "command": "make_msa_arrhenius.sh", "num_cpus": args.cpus, "mem": args.mem})
    base["loader_params"]["MAXCYCLE"] = args.maxcycle
    with open(os.path.join(args.config_dir, "base.yaml"), "w") as fh:
        yaml.safe_dump(base, fh, sort_keys=False)

    jobs = []
    for item in args.fasta:
        tag, fasta = item.split("=", 1)
        fasta = os.path.abspath(fasta)
        for state, n in STATES.items():
            chains = "ABCD"[:n]
            variants = [("apo", None)]
            if state != "tetramer":
                variants += list(LIGANDS.items())
            for lig, sdf in variants:
                job = f"{tag}_{state}_{lig}"
                cfg = {"defaults": ["base"], "job_name": job,
                       "protein_inputs": {c: {"fasta_file": fasta} for c in chains}}
                if sdf:
                    cfg["sm_inputs"] = {"ABCDE"[n]: {
                        "input": os.path.join(os.path.abspath(args.ligand_dir), sdf), "input_type": "sdf"}}
                with open(os.path.join(args.config_dir, job + ".yaml"), "w") as fh:
                    yaml.safe_dump(cfg, fh, sort_keys=False)
                jobs.append((job, tag, n))
    with open(os.path.join(args.config_dir, "jobs.txt"), "w") as fh:
        fh.write("".join(f"{j}\t{t}\t{n}\n" for j, t, n in jobs))
    print(f"wrote base.yaml and {len(jobs)} job configs to {args.config_dir}")
    for i, (j, _, _) in enumerate(jobs, 1):
        print(f"  {i:2d}  {j}")


if __name__ == "__main__":
    main()
