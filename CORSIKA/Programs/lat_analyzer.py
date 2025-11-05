# This program reads binary CORSIKA output files (DATnnnnnn) and generates a formatted text file,
# similar to the original corsikaread.f output for the studying of lateral distribution.

import struct

nome_arquivo_entrada = 'DAT402141'
nome_arquivo_saida = 'Output402141.txt'

PALAVRAS_POR_SUB_BLOCO = 273
SUB_BLOCOS_POR_REGISTRO = 21
PALAVRAS_POR_REGISTRO = PALAVRAS_POR_SUB_BLOCO * SUB_BLOCOS_POR_REGISTRO
BYTES_POR_PALAVRA = 4 
BYTES_POR_REGISTRO = PALAVRAS_POR_REGISTRO * BYTES_POR_PALAVRA

def analisar_arquivo_corsika(arquivo_entrada, arquivo_saida):
    print(f"Iniciando a leitura do arquivo: {arquivo_entrada}")
    
    try:
        with open(arquivo_entrada, 'rb') as f_bin, open(arquivo_saida, 'w') as f_out:
            
            f_out.write(f"READ DATA FROM FILE = {arquivo_entrada}\n")
            num_registro = 0
            
            while True:
                marcador_inicio_bytes = f_bin.read(4)
                if not marcador_inicio_bytes:
                    break
                
                num_registro += 1
                tamanho_registro = struct.unpack('<i', marcador_inicio_bytes)[0]
                
                if tamanho_registro != BYTES_POR_REGISTRO:
                    print(f"  Aviso no Registro {num_registro}: Tamanho inesperado. Pulando...")
                    f_bin.seek(tamanho_registro, 1)
                    f_bin.read(4)
                    continue
                
                dados_bytes = f_bin.read(tamanho_registro)
                f_bin.read(4)

                pdata = struct.unpack(f'<{PALAVRAS_POR_REGISTRO}f', dados_bytes)

                for i in range(0, PALAVRAS_POR_REGISTRO, PALAVRAS_POR_SUB_BLOCO):
                    sub_bloco = pdata[i : i + PALAVRAS_POR_SUB_BLOCO]
                    primeira_palavra = sub_bloco[0]
                    tipo_bloco = 'PARTICULAS'
                    
                    if 211284.0 <= primeira_palavra <= 211286.0: tipo_bloco = 'RUNH'
                    elif 217432.0 <= primeira_palavra <= 217434.0: tipo_bloco = 'EVTH'
                    elif 3396.0 <= primeira_palavra <= 3398.0: tipo_bloco = 'EVTE'
                    elif 3300.0 <= primeira_palavra <= 3302.0: tipo_bloco = 'RUNE'

                    if tipo_bloco == 'RUNH':
                        f_out.write("RUNH\n")
                        vals1 = [sub_bloco[1], sub_bloco[2], sub_bloco[3], sub_bloco[15], sub_bloco[16], sub_bloco[17]]
                        linha1 = "".join([f"{v: 13.5e}" for v in vals1])
                        f_out.write(linha1 + "\n")
                        vals2 = sub_bloco[4:15]
                        linha2 = "".join([f"{v: 11.3e}" for v in vals2])
                        f_out.write(linha2 + "\n")

                    elif tipo_bloco == 'EVTH':
                        f_out.write("EVTH\n")
                        vals = [sub_bloco[1], sub_bloco[2], sub_bloco[3], sub_bloco[6], sub_bloco[10], sub_bloco[11]]
                        linha = "".join([f"{v: 13.5e}" for v in vals])
                        f_out.write(linha + "\n")

                    elif tipo_bloco == 'EVTE':
                        f_out.write("EVTE\n")
                        vals = sub_bloco[1:7]
                        linha = "".join([f"{v: 13.5e}" for v in vals])
                        f_out.write(linha + "\n")

                    elif tipo_bloco == 'RUNE':
                        f_out.write("RUNE\n")
                        vals = sub_bloco[1:3]
                        linha = "".join([f"{v: 13.5e}" for v in vals])
                        f_out.write(linha + "\n")

                    elif tipo_bloco == 'PARTICULAS':
                        for j in range(0, PALAVRAS_POR_SUB_BLOCO, 7):
                            dados_particula = sub_bloco[j : j+7]
                            if dados_particula[0] == 0.0:
                                continue
                            linha = "".join([f"{v: 13.5e}" for v in dados_particula])
                            f_out.write(linha + "\n")
                            
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{arquivo_entrada}' não foi encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return

    print(f"\nExtração concluída. Dados formatados salvos em '{nome_arquivo_saida}'.")

if __name__ == "__main__":
    analisar_arquivo_corsika(nome_arquivo_entrada, nome_arquivo_saida)
