# This program reads particle coordinate data from a CORSIKA simulation output,
# generates a 2D lateral distribution plot of the particle positions.

import matplotlib.pyplot as plt
import numpy as np

nome_arquivo_entrada = 'Output402151.txt'
nome_arquivo_saida = 'distribuicao_lateral.png'

def carregar_dados_particulas(caminho_arquivo):
    print(f"Lendo e processando o arquivo de dados: {caminho_arquivo}...")
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

    print(f"Foram encontradas {len(coords_x)} partículas para o gráfico.")
    return coords_x, coords_y

def gerar_grafico_distribuicao(coords_x, coords_y, nome_saida):
    if not coords_x:
        print("Nenhuma partícula encontrada para gerar o gráfico.")
        return

    print("Gerando o gráfico...")
    coords_x_m = np.array(coords_x) / 100.0
    coords_y_m = np.array(coords_y) / 100.0

    fig, ax = plt.subplots(figsize=(8, 7))
    hist = ax.hist2d(coords_x_m, coords_y_m, bins=200, cmin=1, cmap=plt.cm.jet)
    fig.colorbar(hist[3], ax=ax, label='Contagem de Partículas por Área')

    ax.set_title('Distribuição Lateral de Partículas do Chuveiro', fontsize=16)
    ax.set_xlabel('Posição X [m]', fontsize=12)
    ax.set_ylabel('Posição Y [m]', fontsize=12)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.savefig(nome_saida, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo com sucesso como '{nome_saida}'")

if __name__ == "__main__":
    x, y = carregar_dados_particulas(nome_arquivo_entrada)
    if x is not None:
        gerar_grafico_distribuicao(x, y, nome_arquivo_saida)
