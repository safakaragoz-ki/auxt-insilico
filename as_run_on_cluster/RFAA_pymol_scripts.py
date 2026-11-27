import os

# Directories
input_dir = "/data/karagozm2/RFAA/pdbs"
output_dir = "/data/karagozm2/RFAA/output"
os.makedirs(output_dir, exist_ok=True)

# Define colors for protein chains
chain_colors = {
    "A": "cyan",
    "B": "orange",
    "C": "gold",  # Ligand color
}

# Define rotation angles for different perspectives
view_angles = [0, 90, 180, 270]  # 4 perspectives at 90-degree increments

# Generate PyMOL scripts for each PDB file
for pdb_file in os.listdir(input_dir):
    if not pdb_file.endswith(".pdb"):
        continue

    pdb_path = os.path.join(input_dir, pdb_file)
    base_name = os.path.splitext(pdb_file)[0]

    # Detect structure type from filename
    if "mono" in pdb_file:
        protein_chains = ["A"]  # Mono has only chain A as protein
        ligand_chains = ["B"]  # Mono has chain B as ligand
    elif "dimer" in pdb_file:
        protein_chains = ["A", "B"]  # Dimer has chains A and B as proteins
        ligand_chains = ["C"]  # Dimer has chain C as ligand
    else:
        print(f"Unknown structure type for file {pdb_file}. Skipping...")
        continue

    # PyMOL script content
    pymol_script = f"""
# Open log file
cmd.log_open("/data/karagozm2/RFAA/output/log_{base_name}.txt")

# Load the PDB file
cmd.load("{pdb_path}", "complex")

# Apply distinct colors to protein chains
"""
    # Add coloring for protein chains
    for chain in protein_chains:
        pymol_script += f"""
cmd.select("chain_{chain}", "chain {chain}")
cmd.color("{chain_colors.get(chain, 'white')}", "chain_{chain}")
cmd.show("cartoon", "chain_{chain}")
"""

    # Add ligand handling
    pymol_script += """
# Highlight ligands
"""
    for chain in ligand_chains:
        pymol_script += f"""
cmd.select("chain_{chain}", "chain {chain}")
cmd.color("{chain_colors.get(chain, 'gold')}", "chain_{chain}")
cmd.show("sticks", "chain_{chain}")
"""

    # General settings
    pymol_script += """
# Visualization settings
cmd.bg_color("white")
cmd.set("cartoon_highlight_color", "magenta")
cmd.set("cartoon_side_chain_helper", "on")
cmd.set("cartoon_fancy_helices", "on")
cmd.set("cartoon_fancy_sheets", "on")
cmd.set("cartoon_flat_sheets", 1)
cmd.set("cartoon_smooth_loops", 0)
cmd.set("ray_shadows", "off")
cmd.set("ray_opaque_background", "off")
cmd.set("antialias", 2)
"""

    # Add views for four perspectives
    for angle in view_angles:
        image_file = os.path.join(output_dir, f"visual_{base_name}_view{angle}.png")
        pymol_script += f"""
# Rotate to {angle} degrees
cmd.turn('y', {angle})

# Render image
cmd.ray(2400, 2400)
cmd.png("{image_file}", dpi=300)
"""

    # Close log and exit
    pymol_script += """
cmd.log_close()
cmd.quit()
"""

    # Output script file
    script_file = os.path.join(output_dir, f"{base_name}.pml")

    # Write PyMOL script to file
    with open(script_file, "w") as file:
        file.write(pymol_script)

print(f"Scripts for all PDB files have been created in: {output_dir}")
