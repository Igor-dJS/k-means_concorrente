#!/bin/bash

quantidadeExecucoes=5

# Configurações dos testes
quantidadePontos=("500" "1000" "10000" "100000" "250000" "500000") # Quantidades de pontos nos conjuntos de dados
quantidadeProcessos=("1" "2" "4" "8" "10" "12") # Quantidades de processos a serem testadas
n_clusters=3
n_columns=4

# Diretório para salvar os datasets
datasets_dir="./datasets/${n_clusters}_clusters_${n_columns}_attributes"
mkdir -p "$datasets_dir"

# Diretório para salvar os logs
logs_dir="./logs"

# Caminhos para os logs
log_file="${logs_dir}/log_execucao_kmeans_${n_clusters}_clusters_${n_columns}_attributes.csv"

# Geração de arquivos CSV para cada quantidade de pontos
for pontos in "${quantidadePontos[@]}"; do
    echo "Gerando arquivo de dados com $pontos pontos..."
    python gera_pontos.py $pontos $n_columns "${datasets_dir}/dataset_${pontos}.csv"
done

# Execução do K-Means sequencial
for pontos in "${quantidadePontos[@]}"; do
    for i in $(seq 1 $quantidadeExecucoes); do
        echo "Execução Sequencial - Dataset com $pontos pontos (Execução $i)..."
        python k_means_sequencial_main.py "${datasets_dir}/dataset_${pontos}.csv" $n_clusters "$log_file"
    done
done

# Execução do K-Means concorrente com diferentes números de processos
for processos in "${quantidadeProcessos[@]}"; do
    for pontos in "${quantidadePontos[@]}"; do
        for i in $(seq 1 $quantidadeExecucoes); do
            echo "Execução Concorrente - Dataset com $pontos pontos e $processos processo(s) (Execução $i)..."
            python k_means_concorrente_main.py "${datasets_dir}/dataset_${pontos}.csv" $n_clusters $processos "$log_file"
        done
    done
done

echo "Geração de dados para testes concluída."
