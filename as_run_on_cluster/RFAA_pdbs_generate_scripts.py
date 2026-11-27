import os

# Define your PDB files and their corresponding ligand complexes
pdb_files = {
    "HH103_dimer": [
        "HH103_dimer_4-Cl-IAA.pdb",
        "HH103_dimer_IAA.pdb",
        "HH103_dimer_IBA.pdb",
        "HH103_dimer_PAA_2d.pdb",
    ],
    "HH103_mono": [
        "HH103_mono_4-Cl-IAA.pdb",
        "HH103_mono_IAA.pdb",
        "HH103_mono_IBA.pdb",
        "HH103_mono_PAA_2d.pdb",
    ]
}

# Define the directory to save the generated PyMOL scripts
output_dir = "pymol_scripts_separated"
os.makedirs(output_dir, exist_ok=True)

# Define common PyMOL settings
pymol_settings = """
set ray_trace_mode, 3
set ray_shadows, 0
set antialias, 2
set cartoon_smooth_loops, 1
set cartoon_fancy_helices, 1
set cartoon_highlight_color, grey70
bg_color white
"""

# Function to generate PyMOL script for each complex
def generate_pymol_script(ref_pdb, complex_pdb, output_script):
    with open(output_script, 'w') as f:
        # Load reference and complex structures
        f.write(f"load {ref_pdb}, reference\n")
        f.write(f"load {complex_pdb}, complex\n")
        
        # Align the complex to the reference
        f.write("align complex, reference\n")
        f.write(pymol_settings)

        # Save the reference orientation
        for angle in [0, 90, 180, 270]:
            # Show only the reference structure
            f.write("hide everything\n")
            f.write("show cartoon, reference\n")
            f.write("color cyan, reference\n")
            f.write(f"rotate y, {angle}\n")
            f.write(f"ray 2400, 2400\n")
            f.write(f"png {complex_pdb.split('.')[0]}_ref_{angle}.png\n")

        # Save the complex orientation
        for angle in [0, 90, 180, 270]:
            # Show only the complex structure
            f.write("hide everything\n")
            f.write("show cartoon, complex\n")
            f.write("color orange, complex\n")
            
            # Highlight ligands in the complex
            f.write("select ligand, resn IAA+IBA+Cl-IAA+PAA\n")
            f.write("show sticks, ligand\n")
            f.write("color gold, ligand\n")
            
            f.write(f"rotate y, {angle}\n")
            f.write(f"ray 2400, 2400\n")
            f.write(f"png {complex_pdb.split('.')[0]}_complex_{angle}.png\n")

# Generate scripts for each set of PDB files
for ref_pdb, complexes in pdb_files.items():
    for complex_pdb in complexes:
        output_script = os.path.join(output_dir, f"{complex_pdb.split('.')[0]}_conformation.pml")
        generate_pymol_script(ref_pdb + ".pdb", complex_pdb, output_script)

print("Updated PyMOL scripts generated successfully.")
