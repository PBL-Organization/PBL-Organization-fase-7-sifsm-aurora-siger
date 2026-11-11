SIFSM - Sistema Integrado de Futuro Sustentável em Marte

Repositório oficial do projeto integrador desenvolvido para a colônia espacial Aurora Siger. O sistema unifica backend relacional em SQLite, simulações matemáticas avançadas, automação embarcada com Arduino e arquitetura de agentes autônomos de Inteligência Artificial.

📁 Estrutura do Repositório

codigo_fonte.py: Script principal (Core Backend, CLI interativa, operações CRUD e integração com IA).

automacao_ia.py: Módulo da Frente C contendo o Agente Triador, Agentes Especialistas, Ferramentas e Guardrails.

simulacao_colonia.py: Módulo da Frente B contendo análise estatística com NumPy/Pandas e Regressão Linear Múltipla.

script_banco.sql: Script DDL para estruturação do banco de dados relacional.

dados_aurora_siger.csv: Base de dados tabular utilizada nas simulações analíticas.

requirements.txt: Dependências externas do projeto.

relatorio_tecnico.md: Documentação técnica detalhada da arquitetura.

⚙️ Pré-requisitos e Dependências

O projeto foi desenvolvido utilizando Python 3.10 ou superior.

As únicas bibliotecas externas necessárias são voltadas para computação numérica e manipulação de DataFrames:

numpy

pandas

Instalação das dependências

Execute o seguinte comando no terminal, dentro da pasta raiz do projeto:

pip install -r requirements.txt

Conteúdo do arquivo requirements.txt:

numpy
pandas

🚀 Como Executar o Sistema

Siga os passos abaixo para executar o sistema:

Certifique-se de que o Python está instalado em sua máquina.

Abra o terminal na pasta raiz do projeto.

Execute o script principal do backend unificado:

python codigo_fonte.py

Para executar isoladamente o módulo de simulação matemática e estatística, utilize:

python simulacao_colonia.py

🕹️ Navegação no Menu CLI (codigo_fonte.py)

Ao iniciar o sistema, um menu interativo será exibido no terminal com as seguintes opções:

Cadastrar Novo Módulo (Create): Insere novos registros de infraestrutura com validação de domínio.

Listar Módulos e Diagnóstico (Read): Exibe o painel completo com aplicação de regras booleanas de sustentabilidade.

Alterar Módulo (Update): Modifica parâmetros operacionais de forma inteligente e fluida.

Excluir Módulo (Delete): Remove registros da base com confirmação de segurança.

Consultar IA da Colônia (Agentes): Aciona o Agente Triador, executa handoffs para especialistas e valida guardrails.

Sair: Encerra a sessão com segurança.

SIFSM — Sistema Integrado de Futuro Sustentável em Marte

Tecnologia, inteligência artificial e sustentabilidade a serviço da colonização espacial.