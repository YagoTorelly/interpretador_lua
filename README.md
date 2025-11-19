MEPA/Lua – Interpretador simples em Python

Este é um interpretador mepa para programas de texto, em um formato parecido com Lua. A proposta é direta: você escreve linhas numeradas (10, 20, 30...) com contas e `print`, carrega o arquivo e executa. Também dá para rodar passo a passo e ver os valores das variáveis.


## O que você consegue fazer aqui
- **Carregar** um arquivo de programa (.mepa) com linhas numeradas.
- **Listar** o código que está em memória.
- **Inserir, alterar e remover** linhas do programa.
- **Salvar** o que editou em arquivo.
- **Executar tudo** de uma vez (RUN).
- **Depurar** passo a passo (DEBUG → NEXT) e **ver variáveis** (STACK).


## Requisitos
- **Python 3** instalado. Só isso.


## Como usar no Windows
1) Abra a pasta do projeto: `compilador_meta`  
2) Abra o PowerShell nessa pasta  
3) Execute o interpretador:

```bash
python mepa.py
```

Vai aparecer um prompt. A partir daqui, digite os comandos dentro do próprio programa (não no PowerShell).


## Bora começar com um exemplo
Carregue um exemplo pronto:

```
LOAD tests\ex01.mepa
```

Veja o conteúdo carregado:
```
LIST
```

Execute tudo:
```
RUN
```

Depure (linha a linha):
```
DEBUG
NEXT
STACK
STOP
```

Para sair do programa:
```
EXIT
```


## Escrevendo seu próprio programa
Você pode montar um programa direto no interpretador. Cada linha tem um número e um comando:

```
INS 10 x = 10
INS 20 y = x + 5
INS 30 print(y)
SAVE
RUN
```

Também dá para editar um arquivo `.mepa` em qualquer editor de texto. O formato é simples: cada linha começa com o número da linha, um espaço e o código. Exemplo:

```
10 x = 10
20 y = x + 5
30 print(y)
```


## Comandos essenciais (explicados de forma direta)
- **HELP**: lista os comandos disponíveis
- **LOAD caminho\arquivo.mepa**: carrega um programa do disco
- **LIST**: mostra o que está em memória
- **INS número código**: cria ou substitui a linha indicada
- **DEL número** ou **DEL início fim**: apaga uma linha ou um intervalo
- **SAVE**: salva o programa em um arquivo
- **RUN**: executa o programa inteiro
- **DEBUG**: entra no modo passo a passo
- **NEXT**: roda a próxima linha (no modo DEBUG)
- **STACK**: mostra as variáveis atuais
- **STOP**: sai do modo DEBUG
- **EXIT**: fecha o interpretador


## Dicas úteis
- Se aparecer “Nenhum programa carregado”, use **LOAD** para abrir um arquivo ou **INS** para começar um do zero.
- Ao sair ou carregar outro arquivo com mudanças pendentes, pode aparecer uma pergunta para **salvar**.
- Se der erro na execução, a mensagem indica a **linha** do problema.


## Exemplos incluídos
- `tests\ex01.mepa`
- `tests\ex02.mepa`
- `tests\ex03.mepa`

Abra qualquer um com `LOAD` para testar.


## Integrantes
- Yago Torelly de Araujo | 2300743  
- Leonardo Nunes Madureira | 2301599  
- Lucas Seiti Kawaguti Goto | 2301474  
- Cintia Marques Castanho Sae | 2300255


