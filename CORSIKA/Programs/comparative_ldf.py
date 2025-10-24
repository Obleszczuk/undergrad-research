# This program reads particle coordinate data from multiple CORSIKA simulation outputs,
# calculates the lateral distribution function (LDF) for each primary particle type,
# and generates a comparative plot:
#   - LDF curves for Proton, Carbon, and Iron primaries
#   - Radial distance vs. particle density (logarithmic scale)

import matplotlib.pyplot as plt
import numpy as np

arquivos = {
    "Próton": "Output401151.txt",
    "Carbono": "Output402151.txt",
    "Ferro": "Output403151.txt"
}
nome_arquivo_saida = "distribuicao_radial_ldf_comparacao.png"

def carregar_dados_particulas(caminho_arquivo):
    coords_x = []
    coords_y = []
    
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                if linha.strip().isalpha() or linha.startswith("READ"):
                    continue
                try:
                    partes = linha.split()
                    if len(partes) == 7:
                        coords_x.append(float(partes[4]))
                        coords_y.append(float(partes[5]))
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        print(f"ERRO: Arquivo de entrada '{caminho_arquivo}' não encontrado.")
        return None, None
        
    return np.array(coords_x), np.array(coords_y)

def calcular_ldf(coords_x_cm, coords_y_cm, n_bins=100, r_max=2000):
    if coords_x_cm is None:
        return None, None
    
    distancias_radiais_m = np.sqrt((coords_x_cm/100.0)**2 + (coords_y_cm/100.0)**2)
    bins = np.linspace(0, r_max, n_bins+1)
    contagens, arestas_bins = np.histogram(distancias_radiais_m, bins=bins)
    areas_bins = np.pi * (arestas_bins[1:]**2 - arestas_bins[:-1]**2)
    densidade = np.divide(contagens, areas_bins, out=np.zeros_like(contagens, dtype=float), where=areas_bins!=0)
    centro_bins = (arestas_bins[:-1] + arestas_bins[1:]) / 2.0
    return centro_bins, densidade

def gerar_grafico_comparacao(arquivos, nome_saida):
    fig, ax = plt.subplots(figsize=(10, 6))
    marcadores = ["o", "s", "^"]
    cores = ["tab:blue", "tab:green", "tab:red"]

    print("Processando e plotando os dados de cada partícula primária...")
    for (label, arquivo), marcador, cor in zip(arquivos.items(), marcadores, cores):
        print(f"  - Processando: {label} ({arquivo})")
        x_cm, y_cm = carregar_dados_particulas(arquivo)
        centros, densidade = calcular_ldf(x_cm, y_cm)
        if centros is not None:
            ax.plot(centros, densidade, marker=marcador, linestyle='-', color=cor, label=label)

    ax.set_yscale('log')
    ax.set_title('Função de Distribuição Lateral (LDF) - Comparação', fontsize=16)
    ax.set_xlabel('Distância Radial do Núcleo (r) [m]', fontsize=12)
    ax.set_ylabel('Densidade de Partículas [partículas / m²]', fontsize=12)
    ax.grid(True, which='both', linestyle='--', alpha=0.7)
    ax.legend()
    ax.set_xlim(0, 2000)
    ax.set_ylim(bottom=1e-2)
    plt.savefig(nome_saida, dpi=300, bbox_inches='tight')
    print(f"\nGráfico comparativo salvo com sucesso como '{nome_saida}'")

if __name__ == "__main__":
    gerar_grafico_comparacao(arquivos, nome_arquivo_saida)