"""
SIFSM - Sistema Integrado de Futuro Sustentável em Marte
Arquivo: automacao_ia.py
Descrição: Frente C - Arquitetura de Sistemas Multiagentes, Ferramentas Determinísticas
           e Guardrails de Segurança para a gestão autônoma da colônia Aurora Siger.
"""

import sqlite3
from pathlib import Path

# Caminho para o banco relacional da colônia criado na Frente A
DB_PATH = "aurora_siger.db"


# =====================================================================
# 1. FERRAMENTAS DETERMINÍSTICAS (TOOLS)
# =====================================================================
def ferramenta_consultar_modulo(codigo: str) -> dict:
    """Consulta o banco de dados SQLite para buscar o estado atual de um módulo."""
    if not Path(DB_PATH).exists():
        return {"erro": "Banco de dados não encontrado."}
    
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM modulos_colonia WHERE codigo_modulo = ?", (codigo.upper(),))
    res = cursor.fetchone()
    conexao.close()
    
    if res:
        return dict(res)
    return {"erro": f"Módulo '{codigo}' não encontrado na base de dados."}


# =====================================================================
# 2. GUARDRAILS (FILTROS DE SEGURANÇA)
# =====================================================================
def aplicar_guardrail_seguranca(acao_sugerida: str, dados_modulo: dict) -> tuple[bool, str]:
    """Valida se a decisão tomada pelos agentes respeita os limites operacionais e éticos."""
    tipo = dados_modulo.get("tipo_modulo", "")
    
    # Guardrail crítico: Proibir qualquer corte de energia ou desligamento em sistemas vitais ou médicos
    if "desligar" in acao_sugerida.lower() and tipo in ["Suporte Vital", "Suporte Médico"]:
        return False, "[GUARDRAIL BLOQUEADO] Violação de Protocolo de Segurança: É estritamente proibido desativar módulos de Suporte Vital ou Médico!"
    
    return True, "[GUARDRAIL APROVADO] Ação dentro dos parâmetros de segurança da Aurora Siger."


# =====================================================================
# 3. SISTEMA MULTIAGENTES (ROUTER, ESPECIALISTAS E HANDOFF)
# =====================================================================
class AgenteEspecialistaEnergia:
    """Agente especializado na análise de consumo energético e matrizes da colônia."""
    
    def processar(self, codigo_modulo: str) -> str:
        dados = ferramenta_consultar_modulo(codigo_modulo)
        if "erro" in dados:
            return dados["erro"]
        
        consumo = dados["consumo_kwh"]
        if consumo > 200.0:
            return f"[Agente de Energia] Alerta Crítico: Módulo {codigo_modulo} com consumo elevado ({consumo} kWh). Recomenda-se balanceamento de carga da matriz solar."
        return f"[Agente de Energia] Módulo {codigo_modulo} operando com eficiência energética estável ({consumo} kWh)."


class AgenteEspecialistaAmbiental:
    """Agente especializado em monitoramento térmico, estufas e condições climáticas."""
    
    def processar(self, codigo_modulo: str) -> str:
        dados = ferramenta_consultar_modulo(codigo_modulo)
        if "erro" in dados:
            return dados["erro"]
        
        temp = dados["temperatura_c"]
        if temp > 35.0:
            acao = "desligar subsistema principal" if dados.get("tipo_modulo") == "Energia" else "ativar refrigeração de emergência"
            aprovado, motivo_guardrail = aplicar_guardrail_seguranca(acao, dados)
            
            resultado = f"[Agente Ambiental] Alerta Térmico: Temperatura de {temp}°C detectada no módulo {codigo_modulo}.\n"
            resultado += f"  - Ação Proposta pelo Agente: {acao}\n"
            resultado += f"  - Auditoria do Guardrail: {motivo_guardrail}"
            return resultado
            
        return f"[Agente Ambiental] Módulo {codigo_modulo} com temperatura térmica controlada ({temp}°C)."


class AgenteTriador:
    """Agente Router responsável por receber comandos, interpretar a intenção e fazer o handoff."""
    
    def __init__(self):
        self.especialista_energia = AgenteEspecialistaEnergia()
        self.especialista_ambiental = AgenteEspecialistaAmbiental()

    def gerenciar_solicitacao(self, intent: str, codigo_modulo: str) -> str:
        print(f"\n[Agente Triador] Analisando requisição ('{intent}') para o módulo '{codigo_modulo}'...")
        
        if "energia" in intent.lower() or "consumo" in intent.lower():
            print("[Agente Triador] Handoff realizado -> Direcionando para o Agente de Energia.")
            return self.especialista_energia.processar(codigo_modulo)
            
        elif "temperatura" in intent.lower() or "termico" in intent.lower() or "clima" in intent.lower():
            print("[Agente Triador] Handoff realizado -> Direcionando para o Agente Ambiental.")
            return self.especialista_ambiental.processar(codigo_modulo)
            
        else:
            return "[Agente Triador] Intenção não mapeada para especialistas específicos."


# =====================================================================
# 4. EXECUÇÃO DE TESTE DA ARQUITETURA
# =====================================================================
if __name__ == "__main__":
    print("========================================================")
    print("     SIFSM - SIMULAÇÃO DA ARQUITETURA DE IA E AGENTES   ")
    print("========================================================")
    
    triador = AgenteTriador()
    
    # Cenário 1: Testando o Agente Ambiental em um módulo quente (Matriz Solar)
    resposta_ambiental = triador.gerenciar_solicitacao("temperatura", "MOD-ENG-01")
    print(resposta_ambiental)
    print("-" * 65)
    
    # Cenário 2: Testando o Agente de Energia em um módulo residencial
    resposta_energia = triador.gerenciar_solicitacao("energia", "MOD-HAB-01")
    print(resposta_energia)
    print("========================================================")