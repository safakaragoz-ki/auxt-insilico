# AuxT in silico analysis

Scripts, input files and structural models for the in silico analysis of the
auxin transporter AuxT of *Sinorhizobium fredii* HH103 in

> Moreno-de Castro N, Karagöz MS, Herrero Gómez I, Ayala-García P, Sievers S,
> Müsken M, Giner-Lamia J, Jiménez-Guerrero I, Pérez-Montaño F, Borrero-de Acuña JM.
> *A rhizobial extracellular vesicle-conveyed auxin transporter mediates
> phytohormone mobilization and optimizes rhizobium-legume symbiosis.*
> bioRxiv (2026). https://doi.org/10.64898/2026.07.10.737661

## Contents

| Path | What it is |
|---|---|
| `sequences/` | AuxT sequence as modelled (401 aa, original annotation) and the revised 314-aa sequence without the N-terminal extension (residues 88-401) |
| `ligands/` | SDF files from PubChem: IAA (CID 802), 4-Cl-IAA (CID 100413), IBA (CID 8617), PAA (2D record) |
| `models/apo_alphafold3/` | Ligand-free AuxT monomer, dimer and tetramer (AlphaFold3 server) |
| `models/holo_rfaa/` | AuxT monomer and dimer co-modelled with each ligand (RoseTTAFold All-Atom). Ligand residue name `LG1`; pLDDT (0-1) in the B-factor column; second protomer numbered 402-802 |
| `models/homologs_2024/` | AlphaFold DB models used in the first round of structural alignments (Q9HTA4, B4FSJ4, I1K2H7) |
| `01_rfaa_modelling/` | Slurm script for RFAA inference and config templates |
| `02_apo_holo_comparison/` | Apo vs holo superposition, RMSD, ligand contacts; original PyMOL scripts, logs and contact lists in `original_outputs/` |
| `03_complex_figures/` | PyMOL rendering of the models |
| `04_structural_homologs/` | Pairwise alignment of AuxT with Foldseek hits from the AlphaFold DB; first-round scripts and logs in `original_2024/` |
| `arrhenius/` | Installation, config generation and Slurm scripts to rerun the RFAA modelling with the 314-aa sequence on the NAISS Arrhenius cluster (see `arrhenius/README.md`) |
| `results/` | Tables written by the scripts above |
| `as_run_on_cluster/` | The scripts exactly as they were run (hard-coded cluster paths), kept for provenance |

## Requirements

- RoseTTAFold All-Atom (https://github.com/baker-laboratory/RoseTTAFold-All-Atom) for `01_rfaa_modelling`
- Python >= 3.9 with open-source PyMOL for everything else: `pip install pymol-open-source`

## Usage

Run from the repository root.

```bash
# 1. ligand-bound models (GPU, Slurm); see 01_rfaa_modelling/config_templates/README.md
sbatch 01_rfaa_modelling/run_rfaa.sh HH103_mono_IAA

# 2. apo vs holo: RMSD and ligand contacts -> results/apo_holo_rmsd.csv, results/ligand_contacts_4A.csv
python 02_apo_holo_comparison/apo_holo_analysis.py

# 3. images of all models -> results/figures/
python 03_complex_figures/render_complexes.py

# 4. AuxT (without N-terminal extension) vs AlphaFold DB homologs -> results/structural_homologs/
python 04_structural_homologs/align_homologs.py                      # A0A0H3GMW9, Q9HTA4, A0A0R0ILJ6
python 04_structural_homologs/align_homologs.py --ids P12345 Q67890  # any other UniProt accessions
```

## Notes on the methods

- **Sequence and numbering.** All models were built from the 401-aa sequence of
  the original genome annotation. The first 87 residues are the N-terminal
  extension that is absent from the revised annotation; they are predicted with
  low confidence and do not contact the ligands in the monomer models. Residue
  numbers in the model files and in `original_outputs/` refer to the 401-aa
  sequence; subtract 87 for the revised 314-aa numbering. The result tables give both.
- **RMSD.** Superpositions use PyMOL `align` on all atoms with the default five
  cycles of outlier rejection; the reported value is the RMSD over the atom
  pairs retained after refinement, and the number of those pairs is reported
  with it. `apo_holo_analysis.py` and `align_homologs.py` also report C-alpha
  RMSDs.
- **Ligand contacts.** `results/ligand_contacts_4A.csv` lists residues with any
  atom within 4 Å of the ligand, with their numbers in the model, in the 314-aa sequence and in the 401-aa sequence. The lists in
  `02_apo_holo_comparison/original_outputs/binding_sites/` come from the first
  analysis, which used a 2 Å cutoff; in those files the last entry of each list
  (residue number > 401 in the monomer, > 802 in the dimer) is the ligand itself.
- **Structural homologs.** For the alignments with Foldseek hits the AuxT
  reference is the monomer model truncated to residues 88-401.
- **RFAA configs.** The YAML files in `01_rfaa_modelling/config_templates/` are
  reconstructions of the original configs (see the README in that folder).

## Licence

MIT, see `LICENSE`.
