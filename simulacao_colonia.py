"""
Frente B — Simulação & Matemática do SIFSM.

Este módulo usa o CSV real da Aurora Siger para:
- carregar e validar os dados com Pandas;
- calcular indicadores estatísticos com NumPy;
- simular um cenário de estresse operacional;
- ajustar uma regressão linear múltipla por mínimos quadrados.

Execução:
    python simulacao_colonia.py
    python simulacao_colonia.py --arquivo dados_aurora_siger.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

COLUNAS_OBRIGATORIAS = {
    "codigo_modulo",
    "nome_modulo",
    "tipo_modulo",
    "nivel_critico",
    "consumo_kwh",
    "temperatura_c",
    "status_operacional",
}

COLUNAS_NUMERICAS = ("nivel_critico", "consumo_kwh", "temperatura_c")


def carregar_dados(caminho: str | Path) -> pd.DataFrame:
    """Carrega o CSV e valida sua estrutura e os valores numéricos."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")

    dados = pd.read_csv(caminho)
    ausentes = COLUNAS_OBRIGATORIAS - set(dados.columns)
    if ausentes:
        raise ValueError(
            "O CSV não possui as colunas obrigatórias: "
            + ", ".join(sorted(ausentes))
        )

    for coluna in COLUNAS_NUMERICAS:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    if dados[list(COLUNAS_NUMERICAS)].isna().any().any():
        raise ValueError("Existem valores numéricos ausentes ou inválidos no CSV.")
    if (dados["consumo_kwh"] < 0).any():
        raise ValueError("O consumo em kWh não pode ser negativo.")
    if not dados["nivel_critico"].isin((1, 2, 3)).all():
        raise ValueError("O nível de criticidade deve ser 1, 2 ou 3.")

    return dados


def calcular_indicadores(dados: pd.DataFrame) -> dict[str, float | int]:
    """Calcula indicadores gerais utilizando operações vetorizadas do NumPy."""
    consumo = dados["consumo_kwh"].to_numpy(dtype=float)
    temperatura = dados["temperatura_c"].to_numpy(dtype=float)
    limite_temperatura = 35.0

    return {
        "total_modulos": int(len(dados)),
        "consumo_total_kwh": float(np.sum(consumo)),
        "consumo_medio_kwh": float(np.mean(consumo)),
        "consumo_mediano_kwh": float(np.median(consumo)),
        "desvio_padrao_consumo_kwh": float(np.std(consumo, ddof=0)),
        "temperatura_media_c": float(np.mean(temperatura)),
        "modulos_em_alerta_termico": int(np.count_nonzero(temperatura > limite_temperatura)),
    }


def simular_cenario(
    dados: pd.DataFrame,
    fator_consumo: float = 1.10,
    aumento_temperatura: float = 5.0,
) -> pd.DataFrame:
    """Projeta um cenário de estresse sem alterar o DataFrame original.

    O cenário aplica o mesmo estresse a todos os módulos para facilitar a
    comparação: consumo +10% e temperatura +5 °C por padrão. O resultado
    inclui o diagnóstico calculado a partir dos valores projetados.
    """
    if fator_consumo < 0:
        raise ValueError("O fator de consumo deve ser não negativo.")

    cenario = dados.copy()
    cenario["consumo_simulado_kwh"] = (
        cenario["consumo_kwh"].to_numpy(dtype=float) * fator_consumo
    )
    cenario["temperatura_simulada_c"] = (
        cenario["temperatura_c"].to_numpy(dtype=float) + aumento_temperatura
    )
    cenario["risco_simulado"] = (
        (cenario["temperatura_simulada_c"] > 35.0)
        | (
            (cenario["consumo_simulado_kwh"] > 150.0)
            & (cenario["nivel_critico"] == 3)
        )
    )
    return cenario


def ajustar_regressao_linear(dados: pd.DataFrame) -> dict[str, object]:
    """Ajusta consumo ~ temperatura + criticidade por mínimos quadrados.

    A implementação usa `numpy.linalg.lstsq`, deixando explícito o cálculo
    matemático e evitando uma dependência adicional de machine learning.
    """
    x = dados[["temperatura_c", "nivel_critico"]].to_numpy(dtype=float)
    y = dados["consumo_kwh"].to_numpy(dtype=float)
    matriz_x = np.column_stack((np.ones(len(x)), x))
    coeficientes, _, _, _ = np.linalg.lstsq(matriz_x, y, rcond=None)
    previsoes = matriz_x @ coeficientes

    soma_quadrados_total = np.sum((y - np.mean(y)) ** 2)
    soma_quadrados_residuos = np.sum((y - previsoes) ** 2)
    r2 = 1.0 - (soma_quadrados_residuos / soma_quadrados_total)

    return {
        "intercepto": float(coeficientes[0]),
        "coeficiente_temperatura": float(coeficientes[1]),
        "coeficiente_criticidade": float(coeficientes[2]),
        "r2": float(r2),
        "previsoes_kwh": previsoes,
    }


def prever_consumo(
    temperatura_c: float,
    nivel_critico: int,
    modelo: dict[str, object],
) -> float:
    """Retorna uma previsão de consumo para um módulo hipotético."""
    if nivel_critico not in (1, 2, 3):
        raise ValueError("O nível de criticidade deve ser 1, 2 ou 3.")

    return float(
        modelo["intercepto"]
        + modelo["coeficiente_temperatura"] * temperatura_c
        + modelo["coeficiente_criticidade"] * nivel_critico
    )


def formatar_linha_indicador(nome: str, valor: object) -> str:
    """Formata uma linha do relatório textual para uso no terminal."""
    if isinstance(valor, float):
        return f"{nome}: {valor:.2f}"
    return f"{nome}: {valor}"


def gerar_relatorio(dados: pd.DataFrame) -> str:
    """Gera um relatório textual da análise e da simulação."""
    indicadores = calcular_indicadores(dados)
    cenario = simular_cenario(dados)
    modelo = ajustar_regressao_linear(dados)
    risco = int(cenario["risco_simulado"].sum())

    linhas = [
        "=== FRENTE B — SIMULAÇÃO & MATEMÁTICA ===",
        "",
        "[Indicadores atuais]",
    ]
    linhas.extend(
        formatar_linha_indicador(nome, valor)
        for nome, valor in indicadores.items()
    )
    linhas.extend(
        [
            "",
            "[Cenário de estresse]",
            "Fator de consumo: 1.10 (+10%)",
            "Aumento de temperatura: 5.00 °C",
            f"Módulos em risco no cenário: {risco}",
            "",
            "[Regressão linear: consumo_kwh ~ temperatura_c + nivel_critico]",
            f"Intercepto: {modelo['intercepto']:.4f}",
            f"Coeficiente da temperatura: {modelo['coeficiente_temperatura']:.4f}",
            f"Coeficiente da criticidade: {modelo['coeficiente_criticidade']:.4f}",
            f"R²: {modelo['r2']:.4f}",
        ]
    )
    return "\n".join(linhas)


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--arquivo",
        type=Path,
        default=Path(__file__).with_name("dados_aurora_siger.csv"),
        help="Caminho do CSV com os dados dos módulos.",
    )
    return parser


def main(argumentos: Iterable[str] | None = None) -> None:
    args = construir_parser().parse_args(argumentos)
    dados = carregar_dados(args.arquivo)
    print(gerar_relatorio(dados))


if __name__ == "__main__":
    main()