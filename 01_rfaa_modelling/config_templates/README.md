# RFAA config templates

**These YAML files are reconstructed, not the files used for the original runs.**
The original configs lived in `/data/karagozm2/RFAA/config/inference/` on the cluster
and were not archived. The templates follow the standard RoseTTAFold All-Atom
config layout and reproduce what can be read from the output models:

| job | protein chains | ligand chain | ligand input |
|---|---|---|---|
| `HH103_mono_<ligand>`  | A (401 aa)        | B | `ligands/<ligand>.sdf` |
| `HH103_dimer_<ligand>` | A and B (401 aa each) | C | `ligands/<ligand>.sdf` |

Ligands: `IAA`, `4-Cl-IAA`, `IBA` (PubChem 3D conformers) and `PAA_2d` (PubChem 2D record).
All other RFAA settings were left at the defaults of `base.yaml`.
Copy the templates into the `config/inference/` directory of the RFAA installation
and adjust the relative paths before running `run_rfaa.sh`.
