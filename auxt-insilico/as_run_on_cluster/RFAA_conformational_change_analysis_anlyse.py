import os
from Bio.PDB import PDBParser, NeighborSearch, Atom

# Paths
base_dir = "/data/karagozm2/RFAA"
pdb_dir = os.path.join(base_dir, "pdbs")
output_dir = os.path.join(base_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# Constants
binding_distance = 2.0  # Ångström distance to consider binding

# Function to extract binding sites
def extract_binding_sites(pdb_file, output_file):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)
    atoms = list(structure.get_atoms())
    neighbors = NeighborSearch(atoms)

    ligand_atoms = [atom for atom in atoms if atom.parent.get_resname() not in (
        "ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS", "ILE", 
        "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"
    )]
    
    protein_atoms = [atom for atom in atoms if atom not in ligand_atoms]
    binding_sites = []

    for ligand_atom in ligand_atoms:
        nearby_protein_atoms = neighbors.search(ligand_atom.coord, binding_distance, "A")
        for atom in nearby_protein_atoms:
            if isinstance(atom, Atom.Atom):
                res = atom.get_parent()
                chain_id = res.get_parent().get_id()
                res_id = res.get_id()
                binding_sites.append((chain_id, res_id))

    # Write binding sites to file
    with open(output_file, "w") as f:
        for chain, (hetflag, seq_id, icode) in set(binding_sites):
            f.write(f"Chain {chain}, Residue {seq_id}\n")

# Function to generate PyMOL scripts
def generate_pymol_script(reference_pdb, target_pdb, output_dir, view_command, view_name):
    target_name = os.path.basename(target_pdb).replace('.pdb', '')
    script_name = os.path.join(output_dir, f"align_{target_name}_{view_name}.pml")
    log_file = os.path.join(output_dir, f"log_{target_name}_{view_name}.txt")
    image_file = os.path.join(output_dir, f"alignment_{target_name}_{view_name}.png")

    pymol_script = f"""
# Load reference and target structures
cmd.load("{reference_pdb}", "reference")
cmd.load("{target_pdb}", "target")

# Perform alignment
alignment_rmsd = cmd.align("target", "reference")
rmsd_value = alignment_rmsd[0]
aligned_atoms = alignment_rmsd[1]

# Log RMSD and aligned atoms
cmd.log_open("{log_file}")
cmd.log(f"RMSD: {{rmsd_value}}")
cmd.log(f"Number of aligned atoms: {{aligned_atoms}}")
cmd.log_close()

# Customize visualization
cmd.hide("everything")
cmd.show("cartoon", "reference")
cmd.show("cartoon", "target")
cmd.color("cyan", "reference")
cmd.color("orange", "target")

# Apply the view transformation
{view_command}

# Set view and save high-quality image
cmd.set("ray_shadows", "off")
cmd.set("ray_opaque_background", "off")
cmd.set("antialias", 2)
cmd.ray(2400, 2400)
cmd.png("{image_file}", dpi=300)

# Exit PyMOL
cmd.quit()
"""
    with open(script_name, 'w') as file:
        file.write(pymol_script)

# Function to process all PDB files
def process_pdb_files():
    monomer_file = os.path.join(base_dir, "HH103_monomer.pdb")
    dimer_file = os.path.join(base_dir, "HH103_dimer.pdb")
    
    for pdb_file in os.listdir(pdb_dir):
        if pdb_file.endswith('.pdb'):
            pdb_path = os.path.join(pdb_dir, pdb_file)
            print(f"Processing {pdb_file}...")
            
            # Extract binding sites
            binding_sites_file = os.path.join(output_dir, f"binding_sites_{pdb_file.replace('.pdb', '.txt')}")
            extract_binding_sites(pdb_path, binding_sites_file)
            
            # Generate PyMOL scripts for visualization
            if "mono" in pdb_file:
                generate_pymol_script(monomer_file, pdb_path, output_dir, "", "default")
            elif "dimer" in pdb_file:
                generate_pymol_script(dimer_file, pdb_path, output_dir, "", "default")

# Run the script
process_pdb_files()
