**Relatório do Interpretador de Linguagem Pseudo**

**Grupo:** [Inserir Nomes dos Membros do Grupo]
**Linguagem Escolhida:** Pseudo (linguagem interpretada com escopo estático e dinâmico)

**1. Capa**

- Identificação do Grupo: [Nomes]
- Linguagem Escolhida: Pseudo (implementada em Python)
- Disciplina: [Nome da Disciplina]
- Professor: [Nome do Professor]
- Data: 31 de maio de 2025

**2. Visão Geral da Linguagem Escolhida**

- **Apresentação da Linguagem:**
  - Este projeto foca na implementação de um interpretador para uma linguagem de programação simples, denominada "Pseudo".
  - **Origens e Inspirações:** A linguagem Pseudo foi concebida como um exercício acadêmico para explorar conceitos fundamentais de compiladores e interpretadores, como análise léxica, análise sintática, resolução de escopo (estático e dinâmico) e execução de código. Inspira-se em linguagens imperativas simples com sintaxe C-like.
  - **Principais Características:**
    - Tipagem: Suporta o tipo `int`.
    - Estruturas de Dados: Variáveis simples.
    - Controle de Fluxo: Definição de funções, chamada de funções.
    - Escopo: Suporta escopo estático e dinâmico, selecionável em tempo de execução.
    - Sintaxe: Baseada em C/Java, com declarações de variáveis, definições de funções e blocos de código delimitados por `{}`.
  - **Fundamentos:** O interpretador é construído em Python e segue as fases clássicas:
    1.  **Análise Léxica (`lexer.py`):** Converte o código fonte em uma sequência de tokens.
    2.  **Análise Sintática (`parser.py`):** Constrói uma Árvore Sintática Abstrata (AST) a partir dos tokens.
    3.  **Resolução de Escopo Estático (`scope_resolver.py`):** (Opcional, se o modo estático for selecionado) Analisa a AST para resolver referências de identificadores de acordo com as regras de escopo léxico.
    4.  **Interpretação (`interpreter.py`):** Executa o código percorrendo a AST, utilizando uma pilha de chamadas (`call_stack.py`) e tabelas de símbolos (`symbol_table.py`) para gerenciar o estado do programa.
  - **Funcionalidades:**
    - Declaração de variáveis globais e locais (tipo `int`).
    - Definição de funções com parâmetros.
    - Chamada de funções.
    - Atribuição a variáveis.
    - Expressões simples (literais inteiros, identificadores).
    - Função `print` embutida para saída.
  - **Benefícios:**
    - Permite o estudo prático de diferentes mecanismos de resolução de escopo.
    - Fornece uma base para entender como linguagens de programação são processadas e executadas.
  - **Principais Aplicações:**
    - Ferramenta educacional para o ensino de princípios de linguagens de programação.
    - Protótipo para o desenvolvimento de linguagens de domínio específico mais complexas.

**3. Detalhamento da Linguagem ou Problema**

- **Elementos Desenvolvidos:**
  - **Analisador Léxico (`lexer.py`):**
    - Responsável por tokenizar o código fonte.
    - Exemplo de token: `Token(INT, 'int')`, `Token(ID, 'x')`, `Token(INT_LITERAL, 10)`.
    - Comentário: O lexer utiliza expressões regulares para identificar tokens, o que é uma abordagem comum e eficiente.
  - **Analisador Sintático (`parser.py`):**
    - Constrói a AST (`ast_nodes.py`) usando uma abordagem de descida recursiva.
    - Exemplo de nó AST: `VarDeclNode(var_type='int', var_name='x')`, `FunctionDefNode(name='myFunc', params=[...], body=BlockNode(...))`.
    - Comentário: O parser implementa a gramática da linguagem Pseudo. A estrutura da AST reflete diretamente as construções da linguagem.
  - **Resolvedor de Escopo Estático (`scope_resolver.py`):**
    - Percorre a AST para vincular identificadores às suas declarações, preenchendo `scope_info` nos `IdentifierNode`s. Utiliza `SymbolTable` para rastrear declarações em escopos aninhados.
    - Comentário: Essencial para a correção do escopo estático, garantindo que as variáveis sejam resolvidas no escopo léxico correto.
  - **Interpretador (`interpreter.py`):**
    - Executa o código visitando os nós da AST.
    - Gerencia a pilha de chamadas (`call_stack.py`) com `ActivationRecord`s para cada chamada de função.
    - Utiliza `SymbolTable` para armazenar variáveis globais e locais dentro dos `ActivationRecord`s.
    - Implementa a lógica para escopo estático (usando `lex_parent_frame` e `closure_scope`) e dinâmico (usando `parent_frame`).
    - Exemplo de execução: Ao encontrar um `CallNode`, empilha um novo `ActivationRecord`. Ao encontrar um `IdentifierNode`, busca seu valor na pilha de chamadas (dinâmico) ou seguindo a cadeia léxica (estático).
    - Comentário: O coração do sistema, onde a semântica da linguagem é efetivamente implementada. A distinção clara entre os modos de escopo é um ponto forte.
  - **Estruturas de Dados Auxiliares:**
    - `ast_nodes.py`: Define as classes para os nós da Árvore Sintática Abstrata.
    - `call_stack.py`: Implementa a pilha de chamadas e os registros de ativação.
    - `symbol_table.py`: Implementa a tabela de símbolos para gerenciamento de escopo.
- **Principais Comandos da Linguagem:**
  - `int <nome_variavel>;` (Declaração de variável)
  - `def <nome_funcao>(<param1>, <param2>, ...) { ... }` (Definição de função)
  - `main() { ... }` (Função principal, ponto de entrada)
  - `<variavel> = <expressao>;` (Atribuição)
  - `<nome_funcao>(<arg1>, <arg2>, ...);` (Chamada de função)
  - `print(<expressao>);` (Saída)
- **Exemplos de Elementos:**
  - **Declaração de Variável:**
    ```pseudo
    int x; // Declara uma variável inteira global x
    main() {
      int y; // Declara uma variável inteira local y
      y = 10;
      print(y);
    }
    ```
    - Explicação: `int x;` no escopo global e `int y;` no escopo local da função `main`.
    - Comentário Positivo: Simplicidade na declaração.
    - Comentário Negativo: Suporta apenas um tipo (`int`), limitando a expressividade.
  - **Definição e Chamada de Função:**
    ```pseudo
    int global_var;
    def sum(a, b) {
      int result;
      result = a + b; // Simplificando, não temos operadores binários na AST ainda
      print(result); // Assumindo que 'a+b' seria uma expressão válida
    }
    main() {
      global_var = 5;
      sum(global_var, 3);
    }
    ```
    - Explicação: `sum` é definida e depois chamada de `main`.
    - Comentário Positivo: Mecanismo claro para modularização.
    - Comentário Negativo: A passagem de parâmetros é simples; não há tipos de retorno explícitos além do que pode ser manipulado via variáveis globais ou efeitos colaterais (como `print`).
  - **Escopo Estático vs. Dinâmico (Exemplo `exemple1.pseudo` ou `exemple2.pseudo`):**
    - Analisar o comportamento de `exemple1.pseudo` e `exemple2.pseudo` com os dois modos de escopo.
    - **Escopo Estático:** Variáveis são resolvidas com base na estrutura léxica do código (onde a função foi definida).
      - No `exemple1.pseudo` (ou similar): Se `f` é chamada por `g`, e `f` acessa `x`, ela usará o `x` do escopo onde `f` foi definida (provavelmente global), não o `x` de `g`.
    - **Escopo Dinâmico:** Variáveis são resolvidas com base na cadeia de chamadas de função (quem chamou quem).
      - No `exemple1.pseudo` (ou similar): Se `f` é chamada por `g`, e `f` acessa `x`, ela usará o `x` do escopo de `g` se `g` tiver um `x` local.
    - Comentário: A capacidade de alternar entre os modos de escopo é uma excelente ferramenta de aprendizado. O escopo estático é mais previsível e comum em linguagens modernas, enquanto o dinâmico pode levar a comportamentos mais difíceis de rastrear.
- **Elementos de Orientação a Objetos:**
  - A linguagem Pseudo, na sua forma atual, **não suporta** elementos de Orientação a Objetos (Classes, atributos, herança, polimorfismo).
  - Comentário: Esta é uma limitação de design, focando em aspectos mais procedimentais e de escopo. Adicionar OO seria uma extensão significativa.
- **Elementos de Programação Funcional:**
  - **Funções de Primeira Ordem:** Funções são definidas (`def`) e podem ser chamadas. Elas não são tratadas como cidadãos de primeira classe (não podem ser passadas como argumentos, retornadas de outras funções ou atribuídas a variáveis).
  - **Funções Anônimas (Lambdas):** Não suportadas.
  - **Funções de Alta Ordem:** Não suportadas.
  - **Funções Puras:** É possível escrever funções puras (cujo resultado depende apenas das entradas e não têm efeitos colaterais), mas a linguagem não impõe isso. Ex: uma função `add(a,b)` que apenas retorna `a+b` (se a linguagem tivesse expressões de retorno).
  - **Recursão para Iteração:** A recursão é possível se uma função se chama.
    ```pseudo
    // Exemplo de recursão para simular um loop (fatorial)
    def factorial(n) {
      int temp;
      // Base case: if n is 0 or 1 (simplificando, não temos if)
      // Para demonstração, vamos assumir que n > 1
      // e que a linguagem suportaria uma expressão de retorno ou atribuição
      // temp = n * factorial(n-1); // Isso não é diretamente suportável
      print(n); // Apenas para mostrar a chamada recursiva
      // if (n > 1) { factorial(n-1); } // Precisaria de condicionais
    }
    main() {
      factorial(3); // Esperado: 3, (depois 2, depois 1 se a recursão fosse completa)
    }
    ```
    - Comentário: A ausência de estruturas de controle de fluxo mais ricas (como `if`, `while`) e expressões de retorno limita a aplicabilidade direta de alguns conceitos funcionais.
- **Evolução da Linguagem e Elementos Acrescentados/Modificados:**
  - Descrever o processo de desenvolvimento do interpretador.
  - Inicialmente, pode ter começado com um lexer e parser básicos.
  - Adição do interpretador com um único modo de escopo (ex: dinâmico).
  - Implementação do segundo modo de escopo (estático) e o `StaticScopeResolver`.
  - Refinamentos na AST, tratamento de erros, etc.
  - Crítica: A decisão de suportar ambos os escopos é academicamente valiosa. A falta de tipos de dados mais ricos ou estruturas de controle é uma simplificação intencional para focar nos mecanismos de escopo.

**4. Análise Crítica**

- **Tabela de Critérios e Propriedades:**

| Critério/Propriedade                             | Nota (0-10)                | Justificativa e Comentários (Pontos Favoráveis/Desfavoráveis)                                                                                                                                                                                                                      |
| :----------------------------------------------- | :------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Simplicidade**                                 | 8                          | **Favorável:** Sintaxe mínima, poucas palavras-chave. Fácil de aprender o básico. **Desfavorável:** A simplicidade extrema limita o que pode ser expresso diretamente.                                                                                                             |
| **Ortogonalidade**                               | 5                          | **Favorável:** Conceitos como declaração de variável e chamada de função são relativamente independentes. **Desfavorável:** Interações complexas de escopo podem parecer não ortogonais para iniciantes. Falta de combinação rica de features (ex: tipos + funções de alta ordem). |
| **Expressividade**                               | 3                          | **Desfavorável:** Muito limitada pela ausência de estruturas de controle (if, loops), operadores complexos, tipos de dados ricos, OO, e muitos recursos funcionais. Boa para demonstrar escopo, mas não para programas complexos.                                                  |
| **Adequabilidade**                               | 7 (para fins educacionais) | **Favorável:** Excelente para ensinar sobre análise léxica, sintática, ASTs, tabelas de símbolo, pilhas de chamada e especialmente escopo estático vs. dinâmico. **Desfavorável:** Não adequada para desenvolvimento de software real.                                             |
| **Variedade de Estruturas de Controle**          | 1                          | **Desfavorável:** Apenas sequência e chamada de função. Faltam condicionais e laços.                                                                                                                                                                                               |
| **Mecanismos de Definição de Tipos**             | 2                          | **Favorável:** Permite declarar `int`. **Desfavorável:** Apenas um tipo embutido. Sem tipos definidos pelo usuário, structs, enums, etc.                                                                                                                                           |
| **Suporte à Abstração de Dados**                 | 1                          | **Desfavorável:** Sem classes, módulos ou mecanismos para encapsular dados com operações.                                                                                                                                                                                          |
| **Suporte à Abstração de Processos**             | 6                          | **Favorável:** Funções com parâmetros permitem abstração de processos. **Desfavorável:** Sem funções de primeira/alta ordem, limitando padrões de abstração mais avançados.                                                                                                        |
| **Modelo de Tipos**                              | 3                          | **Favorável:** Simples (apenas `int`), implicitamente estático na declaração. **Desfavorável:** Não há verificação de tipo em tempo de execução além do que o interpretador Python subjacente faria se tipos fossem misturados (o que não é o caso aqui).                          |
| **Portabilidade (do Interpretador)**             | 9                          | **Favorável:** O interpretador é escrito em Python, que é altamente portátil. O código Pseudo em si é interpretado, então roda onde o interpretador rodar.                                                                                                                         |
| **Reusabilidade (do código Pseudo)**             | 3                          | **Desfavorável:** Funções podem ser reutilizadas dentro de um programa Pseudo, mas a falta de um sistema de módulos ou bibliotecas limita a reusabilidade entre projetos.                                                                                                          |
| **Suporte e Documentação (da linguagem Pseudo)** | N/A (interna)              | A documentação é o próprio código do interpretador e este relatório. Para uma linguagem real, seria um fator crítico.                                                                                                                                                              |
| **Tamanho de Código (para tarefas)**             | Baixo (para o que faz)     | **Desfavorável:** Tarefas complexas exigiriam muito código devido à falta de abstrações e estruturas de controle.                                                                                                                                                                  |
| **Generalidade**                                 | 2                          | **Desfavorável:** Linguagem muito específica para fins educacionais de escopo. Não é de propósito geral.                                                                                                                                                                           |
| **Eficiência (de Execução)**                     | 3                          | **Desfavorável:** Sendo interpretada e com a sobrecarga do Python e das estruturas de dados do interpretador (AST, pilha de chamadas), não se espera alta performance.                                                                                                             |
| **Custo (de desenvolvimento do interpretador)**  | Médio                      | **Comentário:** Requer bom entendimento de teoria de compiladores. O custo de usar a linguagem Pseudo é zero.                                                                                                                                                                      |
| **Legibilidade**                                 | 7                          | **Favorável:** Sintaxe simples pode levar a código legível para pequenos programas. **Desfavorável:** Ausência de comentários no código Pseudo (exceto se o lexer os ignorasse) ou estruturas complexas pode dificultar para programas maiores.                                    |

**5. Conclusões**

- **Facilidades Encontradas:**
  - A modularidade do Python facilitou a separação das fases do interpretador (`lexer.py`, `parser.py`, `interpreter.py`).
  - A clareza na definição dos nós da AST (`ast_nodes.py`) ajudou a estruturar o processo de parsing e interpretação.
- **Dificuldades Encontradas:**
  - Implementar corretamente a lógica de busca para escopo estático (cadeia léxica) e dinâmico (cadeia de chamadas) na `interpreter.py` e `call_stack.py`.
  - Garantir que o `StaticScopeResolver` anote corretamente os nós da AST para uso pelo interpretador em modo estático.
  - Debugging de estados da pilha de chamadas e tabelas de símbolo.
- **Benefícios da Linguagem Estudada (Pseudo):**
  - Proporcionou uma compreensão profunda das diferenças conceituais e de implementação entre escopo estático e dinâmico.
  - Serviu como uma excelente ferramenta prática para aplicar conhecimentos teóricos sobre o processamento de linguagens.
- **Problemas e Limitações da Linguagem Pseudo:**
  - Extremamente limitada em termos de tipos de dados, operadores e estruturas de controle, o que a torna impraticável para tarefas reais.
  - Ausência de um sistema de tratamento de erros robusto (além de exceções Python).
  - Falta de recursos de programação funcional e orientada a objetos.

**6. Bibliografia**

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2007). _Compilers: Principles, Techniques, and Tools_ (2nd ed.). Addison-Wesley.
- Friedman, D. P., Wand, M., & Haynes, C. T. (2001). _Essentials of Programming Languages_. MIT Press.
- Nystrom, R. (2021). _Crafting Interpreters_. Genever Benning. (Disponível online)
- Documentação Python (para a implementação do interpretador).
- [Listar quaisquer outras fontes, artigos, ou páginas web consultadas]
