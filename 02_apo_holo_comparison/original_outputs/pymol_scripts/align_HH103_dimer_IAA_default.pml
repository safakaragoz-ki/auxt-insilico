
# Load reference and target structures
cmd.load("/data/karagozm2/RFAA/HH103_dimer.pdb", "reference")
cmd.load("/data/karagozm2/RFAA/pdbs/HH103_dimer_IAA.pdb", "target")

# Perform alignment
alignment_rmsd = cmd.align("target", "reference")
rmsd_value = alignment_rmsd[0]
aligned_atoms = alignment_rmsd[1]

# Log RMSD and aligned atoms
cmd.log_open("/data/karagozm2/RFAA/output/log_HH103_dimer_IAA_default.txt")
cmd.log(f"RMSD: {rmsd_value}")
cmd.log(f"Number of aligned atoms: {aligned_atoms}")
cmd.log_close()

# Customize visualization
cmd.hide("everything")
cmd.show("cartoon", "reference")
cmd.show("cartoon", "target")
cmd.color("cyan", "reference")
cmd.color("orange", "target")

# Apply the view transformation


# Set view and save high-quality image
cmd.set("ray_shadows", "off")
cmd.set("ray_opaque_background", "off")
cmd.set("antialias", 2)
cmd.ray(2400, 2400)
cmd.png("/data/karagozm2/RFAA/output/alignment_HH103_dimer_IAA_default.png", dpi=300)

# Exit PyMOL
cmd.quit()
