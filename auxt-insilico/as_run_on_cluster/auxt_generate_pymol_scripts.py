import os

# Define file paths
reference_pdb = "/data/karagozm2/auxt/HH103_monomer.pdb"
proteins = [
    "/data/karagozm2/auxt/PA_auxt.pdb",
    "/data/karagozm2/auxt/mays_auxt.pdb",
    "/data/karagozm2/auxt/Glycine_max_auxt.pdb",
]

# Define output directory
output_dir = "/data/karagozm2/auxt/output"
os.makedirs(output_dir, exist_ok=True)

# Create PyMOL scripts for different perspectives
for idx, target_pdb in enumerate(proteins, start=1):
    base_name = os.path.basename(target_pdb).replace('.pdb', '')
    
    # Define different view angles and styles
    views = {
        "default": "",
        "rotated": "cmd.turn('y', 90)",
        "closeup": "cmd.zoom('target', 10)",
        "side": "cmd.turn('x', 90)"
    }
    
    for view_name, view_command in views.items():
        script_name = f"align_{base_name}_{view_name}.pml"
        log_file = f"{output_dir}/log_{base_name}_{view_name}.txt"
        image_file = f"{output_dir}/alignment_{base_name}_{view_name}.png"
        rmsd_file = f"{output_dir}/rmsd_values_{base_name}_{view_name}.txt"

        pymol_script = f"""
# Open log file
cmd.log_open("{log_file}")

# Load reference and target structures
cmd.load("{reference_pdb}", "reference")
cmd.load("{target_pdb}", "target")

# Perform alignment and capture RMSD and aligned atoms
alignment_rmsd = cmd.align("target", "reference")
rmsd_value = alignment_rmsd[0]  # RMSD value
aligned_atoms = alignment_rmsd[1]  # Number of aligned atom pairs

# Log RMSD and alignment results to a file
cmd.log("Writing RMSD values...")
cmd.do(f'echo RMSD: {{rmsd_value}} > {rmsd_file}')
cmd.do(f'echo Number of aligned atoms: {{aligned_atoms}} >> {rmsd_file}')

# Customize visualization
cmd.hide("everything")
cmd.show("cartoon", "reference")
cmd.show("cartoon", "target")
cmd.color("cyan", "reference")
cmd.color("orange", "target")

# Background and style settings
cmd.bg_color("white")
cmd.set("cartoon_transparency", 0.2)
cmd.set("cartoon_highlight_color", "magenta")
cmd.set("cartoon_side_chain_helper", "on")
cmd.set("cartoon_fancy_helices", "on")
cmd.set("cartoon_fancy_sheets", "on")
cmd.set("cartoon_flat_sheets", 1)
cmd.set("cartoon_smooth_loops", 0)

# Apply the view transformation
{view_command}

# Adjust view and render
cmd.set("ray_shadows", "off")
cmd.set("ray_opaque_background", "off")
cmd.set("antialias", 2)
cmd.ray(2400, 2400)
cmd.png("{image_file}", dpi=300)

# Close log file and exit PyMOL
cmd.log_close()
cmd.quit()
"""
        # Write PyMOL script to a file
        with open(f"{output_dir}/{script_name}", "w") as file:
            file.write(pymol_script)

print(f"PyMOL scripts for different perspectives have been generated in: {output_dir}")
