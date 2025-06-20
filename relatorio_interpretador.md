# **Relatório Trabalho Final - Modelos de Linguagem de Programação**

**Grupo:** Simulador de Determinação de Escopo

**Linguagem Escolhida Pra Implementação:** Python

# 1. Capa

**Integrantes:** Henrique Carniel da Silva, Marcos Luiz Kurth Reckers, Thiago dos Santos Gonçalves

**Disciplina:** Modelos de Linguagem de Programação (INF01121-U) 

**Professor:** Leandro Krug Wives

**Data:** 25 de junho de 2025

# 2. Visão Geral da Linguagem Escolhida

## **Apresentação da Linguagem**
Nosso projeto focou na implementação de um interpretador para uma linguagem de programação simples. Nossa linguagem foi concebida como um exercício acadêmico para explorar conceitos fundamentais de compiladores e interpretadores, como análise léxica, análise sintática, resolução de escopo (estático e dinâmico) e execução de código. Inspira-se em linguagens imperativas simples com sintaxe C-like.

**Características Principais:**
  - Tipagem: Suporta os tipos `int`, `float` e `char`.
  - Estruturas de Dados: Não possui. Só tem variáveis simples.
  - Controle de Fluxo: Não possui `IF's`, `WHILE's` ou estruturas parecidas.
  - Tipos de escopo: Suporta escopo estático e dinâmico, selecionável em tempo de execução.
  - Sintaxe: Baseada em C/Java, com declarações de variáveis, definições de funções e blocos de código delimitados por `{}`.

**Detalhamento:** O interpretador é construído em Python e segue as fases clássicas:
  1.  **Análise Léxica (`lexer.py`):** Converte o código fonte em uma sequência de tokens.
  2.  **Análise Sintática (`parser.py`):** Constrói uma Árvore Sintática Abstrata (AST) a partir dos tokens.
  3.  **Resolução de Escopo Estático (`scope_resolver.py`):** Analisa a AST para resolver referências de identificadores de acordo com as regras de escopo léxico (Opcional, se o modo estático for selecionado).
  4.  **Interpretação (`interpreter.py`):** Executa o código percorrendo a AST, utilizando uma pilha de chamadas (`call_stack.py`) e tabelas de símbolos (`symbol_table.py`) para gerenciar o estado do programa.

**Funcionalidades:**
  - Declaração de variáveis globais e locais (tipos `int`, `float` e `char`).
  - Definição de funções com e sem parâmetros.
  - Chamada de funções.
  - Operações binárias simples (soma e subtração).
  - Atribuição a variáveis.
  - Expressões simples (literais inteiros, identificadores).
  - Função `print` embutida para saída.
  - Relatório de erros (léxicos, sintáticos e semânticos).

**Objetivos:**

  - Permitir o estudo prático de diferentes mecanismos de resolução de escopo.
  - Fornecer uma base para entender como linguagens de programação são processadas e executadas.


# 3. Detalhamento da Implementação

  **Analisador Léxico (`lexer.py`):**
  - Responsável por tokenizar o código fonte.
  - Exemplo de token: `Token(INT, 'int')`, `Token(ID, 'x')`, `Token(INT_LITERAL, 10)`.
  - O lexer utiliza expressões regulares para identificar tokens, o que é uma abordagem comum e eficiente.
    
  **Analisador Sintático (`parser.py`):**
  
  - Constrói a AST (`ast_nodes.py`) usando uma abordagem de descida recursiva.
  - Exemplo de nó AST: `VarDeclNode(var_type='int', var_name='x')`, `FunctionDefNode(name='myFunc', params=[...], body=BlockNode(...))`.
  - O parser implementa a gramática da nossa linguagem. A estrutura da AST reflete diretamente as construções da linguagem.
    
  **Resolvedor de Escopo Estático (`scope_resolver.py`):**
  
  - Percorre a AST para vincular identificadores às suas declarações, preenchendo `scope_info` nos `IdentifierNode`'s. Utiliza `SymbolTable` para rastrear declarações em escopos aninhados.
  - Essencial para a correção do escopo estático, garantindo que as variáveis sejam resolvidas no escopo léxico correto.

  **Interpretador (`interpreter.py`):**
  - Executa o código visitando os nós da AST.
  - Gerencia a pilha de chamadas (`call_stack.py`) com `ActivationRecord`'s para cada chamada de função.
  - Utiliza `SymbolTable` para armazenar variáveis globais e locais dentro dos `ActivationRecord`'s.
  - Implementa a lógica para escopo estático (usando `lex_parent_frame` e `closure_scope`) e dinâmico (usando `parent_frame`).
  - Exemplo de execução: Ao encontrar um `CallNode`, empilha um novo `ActivationRecord`. Ao encontrar um `IdentifierNode`, busca seu valor na pilha de chamadas (dinâmico) ou seguindo a cadeia léxica (estático).
  - O coração do sistema, onde a semântica da linguagem é efetivamente implementada. A distinção clara entre os modos de escopo é um ponto forte.

  **Estruturas de Dados Auxiliares:**

  - `ast_nodes.py`: Define as classes para os nós da Árvore Sintática Abstrata.
  - `call_stack.py`: Implementa a pilha de chamadas e os registros de ativação.
  - `symbol_table.py`: Implementa a tabela de símbolos para gerenciamento de escopo.
    
**Principais Comandos da Linguagem:**
  - Declaração de variável: `<type> <nome_variavel>;`
  - Definição de função: `def <nome_funcao>(<type> <param1>, <type> <param2>, ...) { ... }`
  - Função principal, ponto de entrada: `main() { ... }`
  - Atribuição: `<variavel> = <expressao>;`
  - Chamada de função: `<nome_funcao>(<arg1>, <arg2>, ...);`
  - Mostra valor na tela: `print(<expressao>);`
  
**Exemplos de Elementos:**
  - **Declaração de Variável:**
    ```pseudo
    int x; // Declara uma variável inteira global x
    main() {
      int y; // Declara uma variável inteira local y
      y = 10;
      print(y);
    }
    ```
  
  - **Definição e Chamada de Função:**

    ```pseudo
    int global_var;
    def mostra_valores(int a, int b) {
      print(a);
      print(b);
    }
    main() {
      global_var = 5;
      mostra_valores(global_var, 3);
    }
    ```

**Guia de Uso:**

  Pra executar em Linux, recomendamos utilizar nosso arquivo ``run.sh``, o qual possui como entrada o nome arquivo na pseudolinguagem. De forma alternativa, é possível executar os comandos a seguir separadamente:
  - ``python3 src/main.py <Nome do Arquivo> --static --json-log <Nome_Do_Log_Estatico.jsonl>``
  - ``python3 src/main.py <Nome do Arquivo> --dynamic --json-log <Nome_Do_Log_Dinamico.jsonl>``
  - ``python3 visualization.py --static-log <Nome_Do_Log_Estatico.jsonl> --dynamic-log <Nome_Do_Log_Dinamico.jsonl> --delay 1.2``

**Bibliotecas e Programas Necessários:**
  - Utilizamos a biblioteca ``rich`` e Python 3.11 pra desenvolver nosso trabalho.
  - Testamos em um computador com Linux Ubuntu 24.04 LTS.
  
# 4. Análise Crítica

## **Tabela de Propriedades da Linguagem:**

| Propriedade | Nota (0-10) | Justificativa e Comentários (Pontos Positivos/Negativos) |
| :--- | :--- | :--- |
| **Simplicidade** | 8 | **Vantagens:** Sintaxe mínima, poucas palavras-chave. Fácil de aprender o básico. **Desvantagens:** A simplicidade extrema limita o que pode ser expresso diretamente. |
| **Ortogonalidade** | 10 | **Vantagens:** Conceitos da linguagem são independentes entre si. |
| **Expressividade** | 3 | **Vantagens:** A linguagem possui operações binárias simples. **Desvantagens:** Muito limitada pela ausência de estruturas de controle (if, loops), operadores complexos, tipos de dados ricos, OO, e muitos recursos funcionais. Boa para demonstrar escopo, mas não para programas complexos. |
| **Mecanismos de Definição de Tipos** | 5 | **Vantagens:** Permite declarar `int`, `char`, e `float`. **Desvantagens:** Poucos tipos embutidos. Sem tipos definidos pelo usuário, structs, enums, etc. |
| **Suporte à Abstração de Dados** | 0 | **Desvantagens:** Sem classes, módulos ou mecanismos para encapsular dados com operações. |
| **Suporte à Abstração de Processos** | 4 | **Vantagens:** Funções com parâmetros permitem abstração de processos. **Desvantagens:** Sem funções de primeira/alta ordem, limitando padrões de abstração mais avançados. Funções não possuem tipo de retorno. |
| **Portabilidade (do Interpretador)** | 9 | **Vantagens:** O interpretador é escrito em Python, que é altamente portátil. O código em si é interpretado, então roda onde o interpretador rodar. |
| **Reusabilidade** | 3 | **Desvantagens:** Funções podem ser reutilizadas dentro de um programa, mas a falta de um sistema de módulos ou bibliotecas limita a reusabilidade entre projetos. |
| **Generalidade** | 2 | **Desvantagens:** Linguagem muito específica para fins educacionais de escopo. Não é de propósito geral. |

# 5. Conclusões

**Pontos Interessantes:**

  - A modularidade do Python facilitou a separação das fases do interpretador (`lexer.py`, `parser.py`, `interpreter.py`).
  - A clareza na definição dos nós da AST (`ast_nodes.py`) ajudou a estruturar o processo de parsing e interpretação.

**Dificuldades:**
  - Implementar corretamente a lógica de busca para escopo estático (cadeia léxica) e dinâmico (cadeia de chamadas) na `interpreter.py` e `call_stack.py` foi complicado.
  - Garantir que o `StaticScopeResolver` anote corretamente os nós da AST para uso pelo interpretador em modo estático.
  - Debugging de estados da pilha de chamadas e tabelas de símbolo.

**Benefícios da Linguagem que Criamos:**
  - Proporcionou uma compreensão profunda das diferenças conceituais e de implementação entre escopo estático e dinâmico.
  - Serviu como uma excelente ferramenta prática para aplicar conhecimentos teóricos sobre o processamento de linguagens.

**Problemas e Limitações da Nossa Linguagem:**
  - Extremamente limitada em termos de tipos de dados, operadores e estruturas de controle, o que a torna inviável para tarefas reais.
  - Ausência de um sistema de tratamento de erros robusto (além de exceções do Python).
  - Falta de recursos de programação funcional e orientada a objetos.

**6. Bibliografia**

- [Documentação Python](https://docs.python.org/3/) (para a implementação do interpretador).
- Trabalhos da disciplina de Compiladores na UFRGS, feitos pelos membros do grupo, como base para criação desse interpretador.