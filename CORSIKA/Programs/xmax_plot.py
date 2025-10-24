# This program reads particle data files from CORSIKA simulations (PAR40##.txt),
# calculates the mean and standard error of the P3 values for each particle type,
# performs linear regression of X_max vs log10(Energy) and generates a plot showing:
#   - Error bars for each particle type (Proton, Carbon, Iron)
#   - Linear trend lines with slopes, intercepts, and R^2 values

import os
import numpy as np
import matplotlib.pyplot as plt
import re
from scipy.stats import linregress

particulas = {
    "1": "Próton",
    "2": "Carbono",
    "3": "Ferro"
}

cores = {
    "Próton": "blue",
    "Carbono": "green",
    "Ferro": "red"
}

pasta_dados = "./dados"
resultados = {part: [] for part in particulas.values()}

for nome_arquivo in os.listdir(pasta_dados):
    match = re.match(r"PAR40([123])(1[456])\.txt", nome_arquivo)
    if not match:
        continue

    tipo = match.group(1)
    energia_str = match.group(2)
    
    logE_eV = int(energia_str)
    logE_GeV = logE_eV - 9

    if tipo == '1' and logE_eV == 14:
        print(f"Ignorando ponto: Próton com energia de 10^{logE_eV} eV (logE_GeV={logE_GeV})")
        continue

    caminho = os.path.join(pasta_dados, nome_arquivo)
    try:
        with open(caminho, 'r') as f:
            dados = np.loadtxt(f, usecols=2)
    except Exception as e:
        print(f"Erro ao ler {nome_arquivo}: {e}")
        continue

    if len(dados) == 0:
        print(f"Arquivo vazio: {nome_arquivo}")
        continue

    media = np.mean(dados)
    erro = np.std(dados) / np.sqrt(len(dados))

    particula = particulas[tipo]
    resultados[particula].append((logE_GeV, media, erro))

plt.figure(figsize=(10, 6))
ax = plt.subplot(111)
legend_labels = []
ordem_particulas = ["Próton", "Carbono", "Ferro"]

for part in ordem_particulas:
    pontos = resultados[part]
    if not pontos or len(pontos) < 2:
        continue
        
    pontos.sort(key=lambda x: x[0])
    logEs, medias, erros = zip(*pontos)
    logEs = np.array(logEs)
    medias = np.array(medias)
    
    line = ax.errorbar(
        logEs, medias, yerr=erros, 
        color=cores[part],
        fmt='o', capsize=5, markersize=5, markeredgewidth=1.5,
        alpha=0.8
    )
    
    reg = linregress(logEs, medias)
    slope, intercept, r_value = reg.slope, reg.intercept, reg.rvalue
    r_squared = r_value ** 2
    
    x_fit = np.linspace(min(logEs), max(logEs), 100)
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, color=cores[part], linestyle='--', linewidth=1.5, alpha=0.7)
    
    label_text = (
        f"$\mathbf{{{part}}}$\n"
        f"$X_{{\max}} = {slope:.2f} \cdot \log_{{10}}(E) + {intercept:.2f}$\n"
        f"$R^2 = {r_squared:.4f}$"
    )
    legend_labels.append((line, label_text))

handles, labels = zip(*legend_labels)

ax.set_xlabel("$\log_{10}(E/\mathrm{GeV})$", fontsize=12)
ax.set_ylabel("$X_{\max} \, (\mathrm{g}/\mathrm{cm}^2)$", fontsize=12)
ax.set_title("Profundidade do máximo de desenvolvimento dos chuveiros", fontsize=14)
ax.grid(True, linestyle="--", alpha=0.7)
ax.legend(handles, labels, loc='upper left', fontsize=9, handlelength=3, framealpha=0.9)

plt.tight_layout()
plt.savefig("grafico_xmax_vs_logE.png", dpi=300)
plt.show()