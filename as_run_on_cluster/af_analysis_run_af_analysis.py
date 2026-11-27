import af_analysis
from af_analysis import analysis, docking
import nglview as nv
import matplotlib.pyplot as plt

# Define the AlphaFold results directory
AF_RESULTS_DIR = "/data/karagozm2/fold_hh103_auxt_dimer"  # Change this to your actual results directory

# Load AlphaFold results
my_data = af_analysis.Data(AF_RESULTS_DIR)

# Calculate structural quality metrics
analysis.pdockq(my_data)
analysis.pdockq2(my_data)
docking.LIS_pep(my_data)

# Save computed metrics to a CSV file
csv_filename = "af_analysis_results.csv"
my_data.df.to_csv(csv_filename, index=False)
print(f"AlphaFold analysis results saved to {csv_filename}")

# Visualizations
print("Generating plots...")

# Plot and save Multiple Sequence Alignment (MSA)
msa_filename = "msa_plot.png"
msa_fig = my_data.plot_msa()
plt.savefig(msa_filename)
plt.close()

# Plot and save pLDDT scores
plddt_filename = "plddt_plot.png"
plddt_fig = my_data.plot_plddt([0, 1])
plt.savefig(plddt_filename)
plt.close()

# Identify best model based on ranking confidence
best_model_index = my_data.df['ranking_confidence'].idxmax()

# Plot and save PAE matrix of the best model
pae_filename = "pae_plot.png"
pae_fig = my_data.plot_pae(best_model_index)
plt.savefig(pae_filename)
plt.close()

print(f"Plots saved as {msa_filename}, {plddt_filename}, and {pae_filename}.")

html_filename = "best_model_3d.html"
png_filename = "best_model_3d.png"
view = my_data.show_3d(best_model_index)
view.download_image(filename=png_filename)  # Save as an image
view._write_html(html_filename)  # Save as an interactive HTML file

print(f"3D model saved as {png_filename} and {html_filename}.")

print("Analysis and visualization complete.")
