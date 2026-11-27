import os

# Directories
input_dir = "/data/karagozm2/RFAA/pdbs/pdbs"
output_dir = "/data/karagozm2/RFAA/pdbs/pdbs"
os.makedirs(output_dir, exist_ok=True)

# Define colors for protein chains
chain_colors = {
    "A": "cyan",
    "B": "orange",
    "C": "gold",  # Ligand color
}

# Views: front (0°) and back (180°)
view_angles = [0, 180]

# Generate PyMOL scripts for each PDB file
for pdb_file in os.listdir(input_dir):
    if not pdb_file.endswith(".pdb"):
        continue

    pdb_path = os.path.join(input_dir, pdb_file)
    base_name = os.path.splitext(pdb_file)[0]

    # Determine chain composition based on file name
    if "mono" in pdb_file:
        protein_chains = ["A"]
        ligand_chains = ["B"] if "IAA" in pdb_file else []
    elif "dimer" in pdb_file:
        protein_chains = ["A", "B"]
        ligand_chains = ["C"] if "IAA" in pdb_file else []
    elif "tetramer" in pdb_file:
        protein_chains = ["A", "B", "C", "D"]
        ligand_chains = []
    else:
        print(f"Skipping unrecognized file type: {pdb_file}")
        continue

    # Start building PyMOL script
    pymol_script = f"""
# Load PDB file
cmd.load("{pdb_path}", "complex")

# Apply colors to protein chains
"""
    for chain in protein_chains:
        pymol_script += f"""
cmd.select("chain_{chain}", "chain {chain}")
cmd.color("{chain_colors.get(chain, 'white')}", "chain_{chain}")
cmd.show("cartoon", "chain_{chain}")
"""

    # Handle ligand chains if present
    for chain in ligand_chains:
        pymol_script += f"""
cmd.select("ligand_{chain}", "chain {chain}")
cmd.color("{chain_colors.get(chain, 'gold')}", "ligand_{chain}")
cmd.show("sticks", "ligand_{chain}")
"""

    # Visualization settings
    pymol_script += """
# Visualization settings
cmd.bg_color("white")
cmd.set("ray_shadows", "off")
cmd.set("antialias", 2)
"""

    # Generate images for defined views
    for angle in view_angles:
        view_label = "front" if angle == 0 else "back"
        image_file = os.path.join(output_dir, f"{base_name}_{view_label}.png")
        pymol_script += f"""
cmd.turn('y', {angle})
cmd.ray(2400, 2400)
cmd.png("{image_file}", dpi=300)
"""

    # End script
    pymol_script += "cmd.quit()\n"

    # Save PyMOL script to file
    script_file = os.path.join(output_dir, f"{base_name}.pml")
    with open(script_file, "w") as script_out:
        script_out.write(pymol_script)

    print(f"Generated PyMOL script for {pdb_file}")

print(f"All PyMOL scripts have been saved to {output_dir}")
