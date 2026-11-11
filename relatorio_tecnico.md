# Relatório Técnico Oficial: Sistema Integrado de Futuro Sustentável em Marte (SIFSM)

## 1. Contexto da Solução
O **SIFSM** foi desenvolvido para suprir as necessidades operacionais e de autonomia da colônia espacial **Aurora Siger**. Em ambientes inóspitos como Marte, a gestão descentralizada e ineficiente de recursos vitais (energia, oxigênio, temperatura e produção agrícola) representa risco iminente à missão. A solução integra persistência relacional, automação de hardware, simulações estocásticas, modelos lineares de previsão e uma camada de inteligência baseada em agentes autônomos.

## 2. Descrição dos Dados e Banco de Dados (Frente A)
A persistência da colônia é estruturada em um banco de dados relacional **SQLite** (`aurora_siger.db`), gerido pelo script DDL `script_banco.sql`. A tabela central `modulos_colonia` armazena os seguintes campos:
* `id`: Chave primária autoincrementada.
* `codigo_modulo`: Identificador único textual (ex: `MOD-HAB-01`).
* `nome_modulo`: Nome descritivo da instalação.
* `tipo_modulo`: Domínio restrito (Habitação, Energia, Agricultura, Laboratório, Suporte Vital, Suporte Médico).
* `nivel_critico`: Escala inteira de criticidade (1 a 3).
* `consumo_kwh`: Carga energética atual em tempo real.
* `temperatura_c`: Métrica térmica monitorada.
* `status_operacional`: Estado atual (OPERACIONAL, ALERTA, MANUTENCAO).

## 3. Regras Lógicas e Automação Embarcada (Frentes A e C)
O sistema aplica regras booleanas de decisão sustentável tanto em nível de software quanto em hardware simulado:
* **Lógica de Software:** Avalia cruzamentos de criticidade e consumo excessivo ($consumo > 150kWh \land criticidade = 3$) ou superaquecimento térmico ($temperatura > 35^\circ C$).
* **Automação Embarcada (Tinkercad):** Simulação de um microcontrolador **Arduino Uno** integrado a um sensor térmico analógico (TMP) e a um atuador visual (LED). O circuito executa a leitura física na borda (*Edge Computing*), disparando alertas locais imediatos em caso de desvios térmicos.

## 4. Estruturas de Dados Aplicadas
Para garantir escalabilidade e eficiência nas buscas, o sistema emprega estruturas de dados otimizadas:
* **Tabelas Hash / Dicionários Python:** Utilizadas no mapeamento do domínio de tipos de módulos e nas consultas indexadas por chave primária no banco.
* **Listas e Tuplas:** Empregadas no armazenamento dinâmico de registros retornados pelo buffer do cursor SQL (`fetchall()`), permitindo iteração linear vetorizada.

## 5. Simulação Computacional e Integração Matemática (Frente B)
Implementada no módulo `simulacao_colonia.py`, a simulação processa a base de dados utilizando **NumPy** e **Pandas**:
* **Indicadores Estatísticos:** Cálculo vetorizado de soma total, média aritmética, mediana e desvio padrão do consumo energético da colônia.
* **Cenário de Estresse:** Projeção estocástica aplicando um fator de majoração de $+10\%$ no consumo e $+5^\circ C$ na temperatura de todos os módulos para testar a resiliência da colônia.

## 6. Modelagem Linear Aplicada
O sistema emprega **regressão linear múltipla por mínimos quadrados** (`numpy.linalg.lstsq`) para estimar o consumo energético em função da temperatura e do nível de criticidade:
* **Variáveis Independentes ($X$):** Temperatura em Celsius e Nível de Criticidade.
* **Variável Dependente ($Y$):** Consumo em kWh.
* **Métrica de Avaliação:** O modelo calcula o coeficiente de determinação ($R^2$) para mensurar a aderência preditiva aos dados reais da colônia.

## 7. Inteligência Artificial e Arquitetura Multiagentes (Frente C)
A IA do SIFSM está estruturada em `automacao_ia.py` sob um modelo de **Sistemas Multiagentes**:
* **Agente Triador (Router):** Analisa a intenção da solicitação da tripulação e executa o *handoff* para o especialista adequado.
* **Agentes Especialistas:** Divididos entre o *Agente de Energia* (focado em matrizes e consumo) e o *Agente Ambiental* (focado em parâmetros térmicos).
* **Ferramentas Determinísticas (Tools):** Funções de acesso direto ao banco SQLite que fornecem o estado real dos módulos aos agentes.
* **Guardrails (Filtros de Segurança):** Mecanismos de auditoria que bloqueiam proibições operacionais críticas (ex: impedir que o sistema desative módulos de Suporte Vital ou Médico).

## 8. Arquitetura Computacional e Eficiência
A solução reflete conceitos de computação de alto desempenho:
* Separação clara entre processamento local na borda (sensores) e processamento analítico centralizado.
* Otimização de consultas relacionais para evitar gargalos de largura de banda e movimentação excessiva de dados entre memória e processador.

## 9. Sustentabilidade, Cidadania Digital e Impacto
* **Uso Responsável:** A simulação prévia de cenários evita desperdícios de recursos antes de intervenções físicas em Marte.
* **Ética e Transparência:** Os dados da tripulação e da colônia são tratados sob rigorosos princípios de privacidade e validação humana obrigatória nas decisões críticas sugeridas pelos agentes.

## 10. Limitações e Trabalhos Futuros
* **Limitações:** O sistema opera com simulações lógicas em ambiente CLI e dados tabulares estáticos/locais.
* **Melhorias Futuras:** Integração de uma API web assíncrona, persistência em banco distribuído em nuvem e conexão com hardwares físicos reais via protocolo MQTT.