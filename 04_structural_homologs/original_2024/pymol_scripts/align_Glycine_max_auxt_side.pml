
# Open log file
cmd.log_open("/data/karagozm2/auxt/output/log_Glycine_max_auxt_side.txt")

# Load reference and target structures
cmd.load("/data/karagozm2/auxt/HH103_monomer.pdb", "reference")
cmd.load("/data/karagozm2/auxt/Glycine_max_auxt.pdb", "target")

# Perform alignment and capture RMSD and aligned atoms
alignment_rmsd = cmd.align("target", "reference")
rmsd_value = alignment_rmsd[0]  # RMSD value
aligned_atoms = alignment_rmsd[1]  # Number of aligned atom pairs

# Log RMSD and alignment results to a file
cmd.log("Writing RMSD values...")
cmd.do(f'echo RMSD: {rmsd_value} > /data/karagozm2/auxt/output/rmsd_values_Glycine_max_auxt_side.txt')
cmd.do(f'echo Number of aligned atoms: {aligned_atoms} >> /data/karagozm2/auxt/output/rmsd_values_Glycine_max_auxt_side.txt')

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
cmd.turn('x', 90)

# Adjust view and render
cmd.set("ray_shadows", "off")
cmd.set("ray_opaque_background", "off")
cmd.set("antialias", 2)
cmd.ray(2400, 2400)
cmd.png("/data/karagozm2/auxt/output/alignment_Glycine_max_auxt_side.png", dpi=300)

# Close log file and exit PyMOL
cmd.log_close()
cmd.quit()
