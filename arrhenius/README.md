# AuxT RFAA reruns on Arrhenius (NAISS)

Reruns the RoseTTAFold All-Atom modelling with the revised 314-aa AuxT sequence
(no N-terminal extension) and adds ligand-free RFAA models, so that apo and holo
models come from the same program:

| # | job | chains |
|---|---|---|
| 1 | `AuxT314_mono_apo` | A |
| 2-5 | `AuxT314_mono_{IAA,4-Cl-IAA,IBA,PAA}` | A + ligand B |
| 6 | `AuxT314_dimer_apo` | A, B |
| 7-10 | `AuxT314_dimer_{IAA,4-Cl-IAA,IBA,PAA}` | A, B + ligand C |
| 11 | `AuxT314_tetramer_apo` | A-D |

`bash make_configs.sh --with-401` adds the same 11 jobs for the original 401-aa
sequence (`AuxT401_*`, array indices 12-22).

**Status: written and checked offline, not yet run on Arrhenius.** Config
generation and Hydra composition were tested against the RFAA source; the
installation, database download and Slurm scripts were not, so expect to adjust
module names and time limits on first use.

## Why two partitions

Arrhenius has x86-64 nodes (`cpu`, `fat`) and aarch64 nodes (`gpu`, NVIDIA GH200).
RFAA's `environment.yaml` and its MSA tools (HH-suite build, PSIPRED, legacy
BLAST, cs-blast) are x86-64 only, and DGL has no current CUDA build for aarch64.

- **Default route: everything on the `cpu` partition.** The official RFAA
  environment installs unchanged; inference runs on CPU cores. AuxT is small
  (314 aa; 628 aa as dimer), so this is slow but practical for 11 jobs.
- **GPU route (experimental):** MSAs on `cpu`, inference on `gpu` with an
  environment built by `setup/03_install_gpu_aarch64_EXPERIMENTAL.sh`, which
  compiles DGL from source. Untested; if the build fails, NAISS support is the
  place to ask. Only worth it if CPU inference turns out too slow.

Accounts: `cpu`/`fat` need a project ending in `-cpu`, `gpu` one ending in `-gpu`
(`projinfo` lists yours).

## Steps

```bash
# 0. put the repository on project storage and edit the first block of settings.sh
cd /nobackup/proj/disk/<project>/ && git clone <your auxt-insilico repo> && cd auxt-insilico/arrhenius
nano settings.sh                      # PROJECT_*, BASE, CONDA_MODULE (ml avail miniforge)

# 1. install RFAA + conda env (x86-64 node with internet; ~30 min)
interactive -A <project>-cpu -p cpu -n 1 -c 8 -t 02:00:00
bash setup/01_install_x86.sh /path/to/RoseTTAFold-All-Atom-main.zip   # or no argument: git clone
exit

# 2. weights + databases (~300 GB unpacked on project storage; check storagequota first)
sbatch -A <project>-cpu setup/02_download_databases.sbatch

# 3. configs (writes $BASE/configs/*.yaml and jobs.txt)
bash make_configs.sh

# 4. MSA + templates, once per sequence
sbatch -A <project>-cpu jobs/1_msa.sbatch

# 5. inference: test the monomer first, then the rest
sbatch -A <project>-cpu --array=1 jobs/2_infer_cpu.sbatch
sbatch -A <project>-cpu --array=2-11 jobs/2_infer_cpu.sbatch

# 6. collect models + confidence table into the repository, then analyse
source settings.sh && activate_x86_env
python collect_results.py "$RUN_DIR"                     # -> models/rfaa_rerun/, results/rfaa_rerun_confidence.csv
pip install pymol-open-source
cd .. && python 02_apo_holo_comparison/apo_holo_analysis.py --rerun models/rfaa_rerun --tag AuxT314
python 04_structural_homologs/align_homologs.py --reference models/rfaa_rerun/AuxT314_mono_apo.pdb --keep-reference-as-is
```

Step 6 writes `results/apo_holo_rmsd_AuxT314.csv`, `results/ligand_contacts_4A_AuxT314.csv`
and `results/structural_homologs/`. The structural alignment with the Foldseek hits
needs no cluster at all: it also runs on a laptop with the AlphaFold3 model
(`python 04_structural_homologs/align_homologs.py`).

## How the configs are built

RFAA reads Hydra YAML files. Every job file starts with `defaults: [base]`, so it
inherits `base.yaml`, and adds a `job_name` plus the inputs:

```yaml
defaults:
- base
job_name: AuxT314_dimer_IAA
protein_inputs:          # one entry per protein chain; the key is the chain letter
  A: {fasta_file: /abs/path/AuxT_HH103_314aa_notail.fasta}
  B: {fasta_file: /abs/path/AuxT_HH103_314aa_notail.fasta}
sm_inputs:               # small molecules; omit the block for apo models
  C: {input: /abs/path/IAA.sdf, input_type: sdf}
```

`make_configs.py` writes these files and a `base.yaml` copied from
`rf2aa/config/inference/base.yaml` with only the paths changed (`output_path`,
`checkpoint_path`, `database_params`). Model and loader parameters stay at the
RFAA defaults (`MAXCYCLE: 4`); `MAXCYCLE=10 bash make_configs.sh` raises the
number of recycles, which the RFAA authors suggest for difficult cases.

Outputs per job in `$BASE/runs/`: `<job>.pdb` (pLDDT 0-1 in the B-factor column)
and `<job>_aux.pt` (pLDDT, PAE, `pae_inter`). RFAA's authors used `pae_inter`
as their main confidence metric and expect good ligand placement below 10.

## Notes

- **MSA reuse.** rf2aa looks for `t000_.msa0.a3m`, `t000_.hhr` and `t000_.atab` in
  `<output_path>/<job_name>/<chain>/` and skips the search if they exist.
  `jobs/1_msa.sbatch` runs the search once per sequence and copies the three files
  into every job/chain folder.
- **SignalP 6** needs a licence and is optional here; AuxT has no signal peptide.
- **BFD** (272 GB) is only searched when UniRef30 gives a shallow alignment. The
  MSA log prints the depth; download BFD only if it is low.
- **Stochasticity.** RFAA randomises the initial template frames, so repeated
  runs of the same config differ. To judge whether an apo/holo difference is
  meaningful, run the apo dimer several times (copy the config under new
  `job_name`s) and compare the spread among those with the apo-holo difference.
- **Conda on Lustre.** The environment has many small files; installation and the
  first import are slow. Keep it on project storage, not in `$HOME` (30 GiB).
