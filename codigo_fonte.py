"""
SIFSM - Sistema Integrado de Futuro Sustentável em Marte
Arquivo: codigo_fonte.py
Descrição: Core Backend finalizado com tratamento de fluxo, validação de domínio
           e atualização inteligente sem perda de dados.
"""

import os
import sqlite3
import sys

# Caminho do banco de dados local da colônia
DB_PATH = "aurora_siger.db"

# Domínio fixo de tipos permitidos para garantir integridade
TIPOS_MODULO = {
    1: "Habitação",
    2: "Energia",
    3: "Agricultura",
    4: "Laboratório",
    5: "Suporte Vital",
    6: "Suporte Médico"
}


def obter_conexao():
    """Retorna uma conexão ativa com o banco SQLite."""
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """Inicializa a tabela e insere dados iniciais (seed) se a base estiver vazia."""
    conexao = None
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS modulos_colonia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_modulo TEXT NOT NULL UNIQUE,
                nome_modulo TEXT NOT NULL,
                tipo_modulo TEXT NOT NULL,
                nivel_critico INTEGER NOT NULL,
                consumo_kwh REAL NOT NULL DEFAULT 0.0,
                temperatura_c REAL NOT NULL DEFAULT 20.0,
                status_operacional TEXT NOT NULL DEFAULT 'OPERACIONAL'
            );
        """
        )
        
        registros_iniciais = [
            ('MOD-HAB-01', 'Habitação Alpha', 'Habitação', 3, 145.5, 22.4, 'OPERACIONAL'),
            ('MOD-AGR-01', 'Estufa Hidropônica 1', 'Agricultura', 2, 88.0, 26.1, 'OPERACIONAL'),
            ('MOD-ENG-01', 'Matriz Solar Principal', 'Energia', 3, 310.2, 45.0, 'ALERTA'),
            ('MOD-LAB-01', 'Laboratório de Pesquisa', 'Laboratório', 1, 62.4, 19.8, 'OPERACIONAL')
        ]
        
        cursor.executemany(
            """
            INSERT OR IGNORE INTO modulos_colonia 
            (codigo_modulo, nome_modulo, tipo_modulo, nivel_critico, consumo_kwh, temperatura_c, status_operacional) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            registros_iniciais
        )
        
        conexao.commit()
    except sqlite3.Error as e:
        print(f"[ERRO DE BANCO] Falha ao inicializar banco de dados: {e}")
    finally:
        if conexao:
            conexao.close()


def ler_entrada_segura(prompt: str, tipo_dado: type):
    """Lê uma entrada do usuário com tratamento de tipo e opção de voltar."""
    while True:
        entrada = input(prompt).strip()
        
        if entrada.lower() in ("voltar", "sair", "cancelar"):
            print("[AVISO] Operação cancelada pelo usuário. Retornando...")
            return None

        if not entrada:
            print("[ALERTA] O campo não pode estar vazio. Tente novamente ou digite 'voltar'.")
            continue

        try:
            if tipo_dado == int:
                return int(entrada)
            elif tipo_dado == float:
                return float(entrada.replace(",", "."))
            else:
                return str(entrada)
        except ValueError:
            print(f"[ERRO DE ENTRADA] Esperado um valor do tipo {tipo_dado.__name__}. Tente novamente.")


def escolher_tipo_modulo():
    """Apresenta um menu numérico limpo para o usuário escolher o tipo de módulo."""
    print("\n--- [SELECIONE O TIPO DE MÓDULO] ---")
    for k, v in TIPOS_MODULO.items():
        print(f" {k}. {v}")
    print("---------------------------------------")
    
    while True:
        escolha = ler_entrada_segura("Escolha o número correspondente ao tipo (ou 'voltar'): ", int)
        if escolha is None:
            return None
        if escolha in TIPOS_MODULO:
            return TIPOS_MODULO[escolha]
        print("[OPÇÃO INVÁLIDA] Selecione um número válido da lista.")


def avaliar_regra_booleana_sustentavel(
    consumo_kwh: float, temperatura_c: float, nivel_critico: int
) -> tuple[bool, str]:
    """Regra Booleana de Decisão Sustentável."""
    alerta_consumo = (consumo_kwh > 150.0) and (nivel_critico == 3)
    alerta_termico = temperatura_c > 35.0
    risco_critico = alerta_consumo or alerta_termico

    if risco_critico:
        motivo = []
        if alerta_consumo:
            motivo.append("Consumo Energético Crítico (>150 kWh)")
        if alerta_termico:
            motivo.append("Superaquecimento (>35°C)")
        return True, " | ".join(motivo)

    return False, "Operação Sustentável Estável"


def cadastrar_modulo():
    """CREATE: Cadastra um novo módulo com validação de domínio."""
    print("\n--- [CADASTRAR NOVO MÓDULO] ---")
    print("Dica: Digite 'voltar' a qualquer momento para cancelar.")

    codigo = ler_entrada_segura("Código do Módulo (ex: MOD-HAB-02): ", str)
    if not codigo: return

    nome = ler_entrada_segura("Nome do Módulo: ", str)
    if not nome: return

    tipo = escolher_tipo_modulo()
    if not tipo: return

    nivel_critico = ler_entrada_segura("Nível de Criticidade (1-Baixo, 2-Médio, 3-Crítico): ", int)
    if nivel_critico is None: return

    consumo = ler_entrada_segura("Consumo Atual (kWh): ", float)
    if consumo is None: return

    temperatura = ler_entrada_segura("Temperatura Atual (°C): ", float)
    if temperatura is None: return

    conexao = None
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO modulos_colonia 
            (codigo_modulo, nome_modulo, tipo_modulo, nivel_critico, consumo_kwh, temperatura_c)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (codigo.upper(), nome, tipo, nivel_critico, consumo, temperatura),
        )
        conexao.commit()
        print(f"[SUCESSO] Módulo '{codigo.upper()}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print(f"[ERRO DE DUPLICIDADE] Já existe um módulo cadastrado com o código '{codigo.upper()}'!")
    except sqlite3.Error as e:
        print(f"[ERRO DE BANCO] Falha ao inserir registro: {e}")
    finally:
        if conexao:
            conexao.close()


def listar_modulos():
    """READ: Listagem completa exibindo explicitamente o TIPO do módulo."""
    print("\n--- [PAINEL DE MÓDULOS DA AURORA SIGER] ---")
    conexao = None
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM modulos_colonia ORDER BY id ASC")
        registros = cursor.fetchall()

        if not registros:
            print("Nenhum módulo registrado no sistema.")
            return

        print("-" * 125)
        print(
            f"{'ID':<4} | {'CÓDIGO':<12} | {'NOME':<22} | {'TIPO':<15} | {'CRIT':<5} | {'kWh':<7} | {'TEMP':<6} | {'DIAGNÓSTICO'}"
        )
        print("-" * 125)

        for reg in registros:
            em_risco, diagnostico = avaliar_regra_booleana_sustentavel(
                reg["consumo_kwh"], reg["temperatura_c"], reg["nivel_critico"]
            )
            status_tag = "[ALERTA]" if em_risco else "[OK]"
            print(
                f"{reg['id']:<4} | {reg['codigo_modulo']:<12} | {reg['nome_modulo']:<22} | "
                f"{reg['tipo_modulo']:<15} | {reg['nivel_critico']:<5} | {reg['consumo_kwh']:<7.1f} | "
                f"{reg['temperatura_c']:<6.1f} | {status_tag} {diagnostico}"
            )
        print("-" * 125)

    except sqlite3.Error as e:
        print(f"[ERRO DE BANCO] Falha ao consultar registros: {e}")
    finally:
        if conexao:
            conexao.close()


def alterar_modulo():
    """UPDATE: Permite alterar nome, tipo, consumo e temperatura de forma segura e fluida."""
    print("\n--- [ALTERAR MÓDULO] ---")
    listar_modulos()
    
    conexao = None
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        codigo = ler_entrada_segura("\nDigite o Código do Módulo que deseja alterar (ou 'voltar'): ", str)
        if not codigo: return

        cursor.execute("SELECT * FROM modulos_colonia WHERE codigo_modulo = ?", (codigo.upper(),))
        registro_atual = cursor.fetchone()
        
        if not registro_atual:
            print(f"[AVISO] Módulo '{codigo.upper()}' não encontrado.")
            return

        print(f"\n[ATUAL] Nome: {registro_atual['nome_modulo']} | Tipo: {registro_atual['tipo_modulo']} | Consumo: {registro_atual['consumo_kwh']}kWh | Temp: {registro_atual['temperatura_c']}°C")
        print("Dica: Pressione Enter sem digitar nada para manter o valor atual.")

        # Atualização do Nome
        novo_nome = input(f"Novo Nome [{registro_atual['nome_modulo']}]: ").strip()
        novo_nome = novo_nome if novo_nome else registro_atual['nome_modulo']

        # Atualização inteligente do Tipo (se desistir, mantém o anterior sem abortar a transação)
        print(f"Tipo Atual: {registro_atual['tipo_modulo']}")
        alterar_tipo = input("Deseja alterar o tipo do módulo? (S/N): ").strip().upper()
        if alterar_tipo == 'S':
            tipo_escolhido = escolher_tipo_modulo()
            # Se o usuário digitar 'voltar' na escolha do tipo, mantemos o tipo atual em vez de cancelar tudo
            novo_tipo = tipo_escolhido if tipo_escolhido is not None else registro_atual['tipo_modulo']
            if tipo_escolhido is None:
                print("[AVISO] Alteração de tipo cancelada. Mantendo o tipo anterior.")
        else:
            novo_tipo = registro_atual['tipo_modulo']

        # Atualização do Consumo
        novo_consumo_str = input(f"Novo Consumo kWh [{registro_atual['consumo_kwh']}]: ").strip()
        novo_consumo = float(novo_consumo_str.replace(",", ".")) if novo_consumo_str else registro_atual['consumo_kwh']

        # Atualização da Temperatura
        nova_temp_str = input(f"Nova Temperatura °C [{registro_atual['temperatura_c']}]: ").strip()
        nova_temp = float(nova_temp_str.replace(",", ".")) if nova_temp_str else registro_atual['temperatura_c']

        cursor.execute(
            """
            UPDATE modulos_colonia 
            SET nome_modulo = ?, tipo_modulo = ?, consumo_kwh = ?, temperatura_c = ?
            WHERE codigo_modulo = ?
        """,
            (novo_nome, novo_tipo, novo_consumo, nova_temp, codigo.upper()),
        )
        conexao.commit()
        print(f"[SUCESSO] Módulo '{codigo.upper()}' atualizado com sucesso!")
    except ValueError:
        print("[ERRO DE ENTRADA] Valor numérico inválido inserido durante a alteração.")
    except sqlite3.Error as e:
        print(f"[ERRO DE BANCO] Falha ao atualizar módulo: {e}")
    finally:
        if conexao:
            conexao.close()


def excluir_modulo():
    """DELETE: Exclui um módulo da colônia."""
    print("\n--- [EXCLUIR MÓDULO DA COLÔNIA] ---")
    listar_modulos()
    
    codigo = ler_entrada_segura("\nDigite o Código do Módulo para EXCLUIR (ou 'voltar'): ", str)
    if not codigo: return

    confirmacao = input(f"Tem certeza que deseja remover '{codigo.upper()}'? (S/N): ").strip().upper()
    if confirmacao != "S":
        print("[CANCELADO] Operação abortada pelo operador.")
        return

    conexao = None
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM modulos_colonia WHERE codigo_modulo = ?", (codigo.upper(),))
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"[SUCESSO] Módulo '{codigo.upper()}' removido da base de dados.")
        else:
            print(f"[AVISO] Módulo '{codigo.upper()}' não foi encontrado.")
    except sqlite3.Error as e:
        print(f"[ERRO DE BANCO] Falha ao excluir registro: {e}")
    finally:
        if conexao:
            conexao.close()


def menu_principal():
    """Menu CLI interativo do SIFSM."""
    inicializar_banco()

    while True:
        print("\n========================================================")
        print("    SIFSM - SISTEMA INTEGRADO SUSTENTÁVEL EM MARTE      ")
        print("========================================================")
        print(" 1. Cadastrar Novo Módulo (Create)")
        print(" 2. Listar Módulos e Diagnóstico Sustentável (Read)")
        print(" 3. Alterar Módulo (Nome, Tipo, Consumo, Temp) (Update)")
        print(" 4. Excluir Módulo da Colônia (Delete)")
        print(" 5. Sair do Sistema")
        print("========================================================")

        opcao = ler_entrada_segura("Escolha uma opção (1-5): ", int)
        
        if opcao is None:
            continue
        
        if opcao == 1:
            cadastrar_modulo()
        elif opcao == 2:
            listar_modulos()
        elif opcao == 3:
            alterar_modulo()
        elif opcao == 4:
            excluir_modulo()
        elif opcao == 5:
            print("\n[ENCERRANDO] Fechando conexão com o SIFSM. Até logo!")
            sys.exit(0)
        else:
            print("[OPÇÃO INVÁLIDA] Digite um número de 1 a 5.")


if __name__ == "__main__":
    menu_principal()