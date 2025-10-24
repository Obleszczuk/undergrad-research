# This program reads CORSIKA's detailed shower output (OUT######.txt) and Hillas parameter files (PAR######.txt),
# performs numerical analysis, and generates plots for particle and energy profiles:
#   - Longitudinal profiles of electrons and photons with mean and standard deviation
#   - Histograms of Gaisser–Hillas parameters (N_max, X_0, X_max) with peak indicators

import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

file_path = "OUT40315.txt"
par_file = "PAR40315.txt"

dados_chuveiros = []

re_inicio = re.compile(r"# SHOWER (\d+)")
re_hillas = re.compile(r"# Hillas parameters: (.+)")
re_chi2 = re.compile(r"# chi2/dof= (\S+) avdev= (\S+)")

with open(file_path, "r") as f:
    lines = f.readlines()

chuveiro_atual = None
secao = None

for line in lines:
    line = line.strip()

    match_inicio = re_inicio.match(line)
    if match_inicio:
        if chuveiro_atual:
            dados_chuveiros.append(chuveiro_atual)
        chuveiro_atual = {"id": int(match_inicio.group(1)), "particles": [], "energy": [], "hillas": None, "chi2": None}
        continue

    if "Longitudinal particle distribution" in line:
        secao = "particles"
        continue
    if "Energy deposit distribution" in line:
        secao = "energy"
        continue
    if match := re_hillas.match(line):
        chuveiro_atual["hillas"] = list(map(float, match.group(1).split()))
        continue
    if match := re_chi2.match(line):
        chuveiro_atual["chi2"] = (float(match.group(1)), float(match.group(2)))
        continue
    if "# End of shower" in line:
        secao = None
        continue

    if secao and chuveiro_atual:
        valores = list(map(float, line.split()))
        chuveiro_atual[secao].append(valores)

if chuveiro_atual:
    dados_chuveiros.append(chuveiro_atual)

print(f"Total de chuveiros carregados: {len(dados_chuveiros)}")

all_depths = np.array([chuveiro["particles"] for chuveiro in dados_chuveiros])

mean_profile = np.mean(all_depths, axis=0)
std_profile = np.std(all_depths, axis=0)

depths = mean_profile[:, 0]
mean_electrons = mean_profile[:, 3]
std_electrons = std_profile[:, 3]
mean_photons = mean_profile[:, 1]
std_photons = std_profile[:, 1]

max_electrons_idx = np.argmax(mean_electrons)
max_electrons_depth = depths[max_electrons_idx]
max_electrons_value = mean_electrons[max_electrons_idx]

plt.figure(figsize=(8,6))
plt.plot(depths, mean_electrons, label="Perfil Médio de Elétrons", color="r")
plt.fill_between(depths, mean_electrons - std_electrons, mean_electrons + std_electrons, color="r", alpha=0.2, label="±1σ")
plt.scatter(max_electrons_depth, max_electrons_value, color="black", zorder=3)
plt.text(max_electrons_depth, max_electrons_value, f"({max_electrons_depth:.1f}, {max_electrons_value:.1e})", fontsize=10, verticalalignment='bottom')
plt.xlabel("Profundidade Atmosférica (g/cm²)")
plt.ylabel("Número Médio de Elétrons")
plt.title("Perfil Médio do Número de Elétrons")
plt.legend()
plt.grid()
plt.show()

max_photons_idx = np.argmax(mean_photons)
max_photons_depth = depths[max_photons_idx]
max_photons_value = mean_photons[max_photons_idx]

plt.figure(figsize=(8,6))
plt.plot(depths, mean_photons, label="Perfil Médio de Fótons", color="b")
plt.fill_between(depths, mean_photons - std_photons, mean_photons + std_photons, color="b", alpha=0.2, label="±1σ")
plt.scatter(max_photons_depth, max_photons_value, color="black", zorder=3)
plt.text(max_photons_depth, max_photons_value, f"({max_photons_depth:.1f}, {max_photons_value:.1e})", fontsize=10, verticalalignment='bottom')
plt.xlabel("Profundidade Atmosférica (g/cm²)")
plt.ylabel("Número Médio de Fótons")
plt.title("Perfil Médio do Número de Fótons")
plt.legend()
plt.grid()
plt.show()

data = np.loadtxt(par_file)

P1, P2, P3 = data[:, 0], data[:, 1], data[:, 2]

def plot_histogram(ax, data, bins, color, xlabel, title):
    counts, bin_edges = np.histogram(data, bins=bins)
    max_idx = np.argmax(counts)
    peak_value = (bin_edges[max_idx] + bin_edges[max_idx + 1]) / 2
    ax.hist(data, bins=bins, color=color, alpha=0.7, edgecolor='black')
    ax.axvline(peak_value, color='k', linestyle='dashed', linewidth=1.5, label=f"Pico: {peak_value:.2f}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequência")
    ax.set_title(title)
    ax.legend()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

plot_histogram(axes[0], P1 / 1000, bins=30, color='b', xlabel=r"$N_{\max}$ ($\times 10^3$)", title="Número máximo de partículas")
plot_histogram(axes[1], P2, bins=30, color='g', xlabel=r"$X_0$ (g/cm²)", title="Profundidade inicial efetiva")
plot_histogram(axes[2], P3, bins=30, color='r', xlabel=r"$X_{\max}$ (g/cm²)", title="Profundidade do máximo de desenvolvimento")

plt.tight_layout()
plt.show()