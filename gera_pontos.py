import sys
import numpy as np
import pandas as pd

def gera_pontos_csv(qtd_pontos, qtd_colunas, output_file):
    """
    Gera um conjunto de pontos aleatórios com a quantidade especificada de colunas e salva em formato CSV.

    Args:
        qtd_pontos (int): Quantidade de pontos a serem gerados.
        qtd_colunas (int): Quantidade de colunas no arquivo CSV.
        output_file (str): Nome do arquivo CSV de saída.
    """
    # Gera uma matriz com qtd_pontos linhas e qtd_colunas colunas, com valores entre 0 e 10
    dados = np.random.uniform(0, 10, (qtd_pontos, qtd_colunas))
    
    # Cria nomes de colunas dinamicamente
    colunas = [f"Coluna{i+1}" for i in range(qtd_colunas)]
    
    # Converte para DataFrame para salvar em CSV
    df = pd.DataFrame(dados, columns=colunas)
    df.to_csv(output_file, index=False)
    print(f"Arquivo '{output_file}' gerado com {qtd_pontos} pontos e {qtd_colunas} colunas.")

if __name__ == "__main__":
    # Verifica se os argumentos necessários foram passados
    if len(sys.argv) != 4:
        print("Uso: python gera_pontos.py <quantidade_pontos> <quantidade_colunas> <arquivo_saida>")
        sys.exit(1)
    
    try:
        # Lê os argumentos
        qtd_pontos = int(sys.argv[1])
        qtd_colunas = int(sys.argv[2])
        output_file = sys.argv[3]

        # Verifica se as entradas são válidas
        if qtd_pontos <= 0 or qtd_colunas <= 0:
            raise ValueError("Quantidade de pontos e colunas deve ser maior que zero.")
        
        # Gera os pontos e salva no arquivo CSV
        gera_pontos_csv(qtd_pontos, qtd_colunas, output_file)
    except ValueError as e:
        print(f"Erro: {e}")
        sys.exit(1)
