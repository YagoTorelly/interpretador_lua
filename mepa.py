#!/usr/bin/env python3
"""

Integrantes do Grupo:

- Yago Torelly de Araujo | 2300743
- Leonardo Nunes Madureira | 2301599
- Lucas Seiti Kawaguti Goto | 2301474
- Cintia Marques Castanho Sae | 2300255


Divisorias principais do interpretador MEPA 

1) ESTADO GLOBAL DO INTERPRETADOR
   - Variáveis que representam o programa carregado, arquivo atual,
     modo debug, contador de linha e memória de variáveis.

2) FUNÇÕES UTILITÁRIAS
   - Funções auxiliares para lidar com entrada do usuário, controle de
     alterações não salvas e ordenação de linhas.

3) COMANDOS DO REPL (LOAD, LIST, INS, DEL, SAVE)
   - Conjunto de funções que manipulam o código-fonte em memória
     e fazem leitura/gravação em arquivo.

4) INTERPRETADOR mini-Lua
   - Funções responsáveis por executar UMA linha da linguagem
     (atribuições e print) e por percorrer o programa sequencialmente.

5) MODO DEBUG (DEBUG, NEXT, STACK, STOP)
   - Controle de execução passo a passo, mantendo um program_counter
     e exibindo o estado das variáveis.

6) LOOP PRINCIPAL (REPL)
   - Laço que lê comandos do usuário, interpreta e chama as funções
     acima, exibindo um prompt interativo.
"""

import os
import sys
from typing import Dict, Optional, Tuple


# =====================================================================
# 1. ESTADO GLOBAL DO REPL / INTERPRETADOR
# =====================================================================
# Aqui definimos variáveis globais que representam:
# - o arquivo atual associado ao programa (current_file),
# - se existem alterações não salvas (dirty),
# - o código do programa em memória (program_lines),
# - o modo de execução (debug_mode, program_counter),
# - e o ambiente de variáveis em tempo de execução (runtime_env).
# =====================================================================

current_file: Optional[str] = None  # caminho do arquivo aberto
dirty: bool = False                 # há alterações não salvas?

# programa em memória: {numero_linha: "código"}
program_lines: Dict[int, str] = {}

# estado de execução / debug
debug_mode: bool = False
program_counter: Optional[int] = None  # linha atual (número da linha)
runtime_env: Dict[str, object] = {}    # "memória" de variáveis


# =====================================================================
# 2. FUNÇÕES UTILITÁRIAS
# =====================================================================
# Funções de apoio usadas por vários comandos:
# - marcação de alterações (dirty),
# - confirmação de descarte de mudanças,
# - conversão segura para int,
# - obtenção de linhas ordenadas.
# =====================================================================


def mark_dirty() -> None:
    """Marca o programa como 'alterado' (há mudanças não salvas)."""
    global dirty
    dirty = True


def clear_dirty() -> None:
    """Marca que não há alterações pendentes (após LOAD ou SAVE)."""
    global dirty
    dirty = False


def ask_yes_no(msg: str) -> bool:
    """Pergunta [s/N] e retorna True se usuário responder 's'."""
    ans = input(f"{msg} [s/N] ").strip().lower()
    return ans in ("s", "sim", "y", "yes")


def ensure_can_discard_changes() -> bool:
    """
    Se houver alterações não salvas, pergunta se pode descartar
    (oferecendo a opção de salvar antes).

    Retorna True se pode continuar a operação,
    ou False se o usuário cancelar ou algo der errado.
    """
    if not dirty:
        return True
    if ask_yes_no("Há alterações não salvas. Deseja salvar antes?"):
        if not cmd_save():
            # erro ou cancelado
            return False
        return True
    else:
        # usuário não quis salvar, mas permite continuar
        return True


def parse_int(value: str) -> Optional[int]:
    """Tenta converter para int; em caso de falha, retorna None."""
    try:
        return int(value)
    except ValueError:
        return None


def sorted_line_numbers():
    """Retorna a lista de números de linha do programa em ordem crescente."""
    return sorted(program_lines.keys())


# =====================================================================
# 3. COMANDOS DO REPL (EDIÇÃO E ARQUIVOS)
# =====================================================================
# Este bloco contém as funções que implementam os comandos:
# LOAD, LIST, INS, DEL, SAVE.
# São responsáveis por carregar/salvar código, listar, inserir e
# remover linhas do programa em memória.
# =====================================================================


def cmd_load(path: str) -> None:
    """
    Comando LOAD.
    Carrega um arquivo de código numerado (formato: '<linha> <código>')
    e o armazena em program_lines.
    """
    global current_file, program_lines, debug_mode, program_counter, runtime_env

    # Antes de trocar o programa, verifica alterações não salvas
    if not ensure_can_discard_changes():
        print("Operação LOAD cancelada.")
        return

    if not os.path.exists(path):
        print(f"Erro: arquivo '{path}' não encontrado.")
        return

    try:
        new_program: Dict[int, str] = {}
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                if not line.strip():
                    continue
                # Espera algo como: 10 x = 1
                parts = line.split(maxsplit=1)
                if len(parts) != 2:
                    print(f"Aviso: linha ignorada (sem número + código): {line}")
                    continue
                num_str, code = parts
                num = parse_int(num_str)
                if num is None or num < 0:
                    print(f"Aviso: número de linha inválido: {line}")
                    continue
                new_program[num] = code

        program_lines = new_program
        current_file = path
        clear_dirty()

        # reset estado de execução
        debug_mode = False
        program_counter = None
        runtime_env = {}

        print(f"Arquivo '{path}' carregado com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")


def cmd_list() -> None:
    """
    Comando LIST.
    Lista o programa em memória, exibindo 20 linhas por 'página'.
    """
    if not program_lines:
        print("Nenhum programa carregado.")
        return

    nums = sorted_line_numbers()
    page_size = 20
    for i in range(0, len(nums), page_size):
        chunk = nums[i:i + page_size]
        for n in chunk:
            print(f"{n:4d} {program_lines[n]}")
        if i + page_size < len(nums):
            input("-- pressione ENTER para continuar --")


def cmd_ins(line_no: int, code: str) -> None:
    """
    Comando INS.
    Insere ou substitui a linha 'line_no' pelo código fornecido.
    """
    existed = line_no in program_lines
    old = program_lines.get(line_no)
    program_lines[line_no] = code
    mark_dirty()

    if existed:
        print(f"Linha {line_no} substituída.")
        print(f"   De: {old}")
        print(f"   Para: {code}")
    else:
        print(f"Linha {line_no} inserida: {code}")


def cmd_del_single(line_no: int) -> None:
    """
    Comando DEL com um único número de linha.
    Remove uma linha específica do programa.
    """
    if line_no not in program_lines:
        print(f"Erro: linha {line_no} inexistente.")
        return
    removed = program_lines.pop(line_no)
    mark_dirty()
    print(f"Linha {line_no} removida: {removed}")


def cmd_del_range(start_no: int, end_no: int) -> None:
    """
    Comando DEL com intervalo.
    Remove todas as linhas entre start_no e end_no (inclusive).
    """
    if start_no > end_no:
        print("Erro: intervalo inválido (linha inicial maior que final).")
        return
    to_remove = [n for n in program_lines.keys() if start_no <= n <= end_no]
    if not to_remove:
        print("Nenhuma linha no intervalo especificado.")
        return
    for n in sorted(to_remove):
        print(f"Removendo linha {n}: {program_lines[n]}")
        program_lines.pop(n)
    mark_dirty()


def cmd_save() -> bool:
    """
    Comando SAVE.
    Salva o programa em disco no arquivo atual.
    Retorna True se salvou com sucesso, False em caso de erro.
    """
    global current_file
    if not program_lines:
        print("Nenhum programa em memória para salvar.")
        return False

    if current_file is None:
        path = input("Informe o nome do arquivo para salvar: ").strip()
        if not path:
            print("Operação SAVE cancelada (nome vazio).")
            return False
        current_file = path

    try:
        with open(current_file, "w", encoding="utf-8") as f:
            for n in sorted_line_numbers():
                f.write(f"{n} {program_lines[n]}\n")
        clear_dirty()
        print(f"Arquivo '{current_file}' salvo com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return False


# =====================================================================
# 4. INTERPRETADOR MINI-LUA (EXECUÇÃO)
# =====================================================================
# Este bloco contém o núcleo do "interpretador":
# - reset_runtime: prepara ambiente de execução e program_counter;
# - eval_expression: avalia expressões aritméticas usando eval;
# - execute_line: interpreta UMA linha de código (atribuição/print);
# - run_sequential: executa o programa por completo ou prepara para DEBUG.
# =====================================================================


def reset_runtime():
    """
    Reinicia o ambiente de execução:
    - limpa as variáveis (runtime_env),
    - posiciona o program_counter na primeira linha existente.
    """
    global runtime_env, program_counter
    runtime_env = {}
    pc_list = sorted_line_numbers()
    program_counter = pc_list[0] if pc_list else None


def eval_expression(expr: str) -> object:
    """
    Avalia uma expressão da nossa mini-Lua usando eval do Python.

    ATENÇÃO: isso não é Lua de verdade, mas um subconjunto bem parecido:
      - +, -, *, /, parênteses
      - nomes de variáveis iguais

    O escopo usado é somente o dicionário de variáveis runtime_env.
    """
    try:
        value = eval(expr, {}, runtime_env)
        return value
    except Exception as e:
        raise RuntimeError(f"Erro ao avaliar expressão '{expr}': {e}")


def execute_line(code: str) -> None:
    """
    Executa UMA linha de código da mini-Lua.
    Suporta:
        - local x = expr
        - x = expr
        - print(expr)
    """
    stripped = code.strip()
    if not stripped:
        return

    # Trata "local x = ..." como "x = ..."
    if stripped.startswith("local "):
        stripped = stripped[len("local "):].lstrip()

    # print(...)
    if stripped.startswith("print(") and stripped.endswith(")"):
        inner = stripped[len("print("):-1].strip()
        value = eval_expression(inner)
        print(value)
        return

    # Atribuição: x = expr
    if "=" in stripped:
        var_name, expr = stripped.split("=", 1)
        var_name = var_name.strip()
        expr = expr.strip()
        if not var_name.isidentifier():
            raise RuntimeError(f"Nome de variável inválido: '{var_name}'")
        value = eval_expression(expr)
        runtime_env[var_name] = value
        return

    # Caso não reconheça a sintaxe:
    raise RuntimeError(f"Instrução não suportada: '{code}'")


def run_sequential(debug: bool = False) -> None:
    """
    Executa o programa sequencialmente.

    - Se debug=False (comando RUN):
        executa todas as linhas em ordem, do início ao fim.

    - Se debug=True (comando DEBUG):
        apenas configura o estado para execução passo a passo
        (program_counter) e exibe a linha inicial; a execução em si
        é feita pela função debug_next().
    """
    global program_counter

    if not program_lines:
        print("Nenhum programa carregado.")
        return

    if not debug:
        # RUN: executa tudo de uma vez
        reset_runtime()
        for n in sorted_line_numbers():
            code = program_lines[n]
            try:
                execute_line(code)
            except RuntimeError as e:
                print(f"Erro na linha {n}: {e}")
                return
        print("Execução finalizada.")
    else:
        # DEBUG: só posiciona para a primeira linha
        if program_counter is None:
            reset_runtime()
        # O resto é controlado por NEXT
        if program_counter is None:
            print("Não há linhas para executar.")
        else:
            print(f"Modo DEBUG: pronto na linha {program_counter}.")


# =====================================================================
# 5. MODO DEBUG (NEXT / STACK / STOP)
# =====================================================================
# Conjunto de funções voltadas à execução passo a passo:
# - debug_next: executa somente a próxima linha;
# - show_stack: mostra o estado atual das variáveis;
# - stop_debug: sai do modo debug e reseta program_counter.
# =====================================================================


def debug_next() -> None:
    """Executa a próxima linha no modo DEBUG."""
    global program_counter

    if program_counter is None:
        print("Nenhuma linha pronta para executar (DEBUG).")
        return

    nums = sorted_line_numbers()
    if program_counter not in nums:
        print("Program counter inválido, reiniciando debug.")
        reset_runtime()
        if program_counter is None:
            print("Não há linhas para executar.")
            return

    idx = nums.index(program_counter)
    line_no = nums[idx]
    code = program_lines[line_no]
    print(f"[DEBUG] Executando linha {line_no}: {code}")
    try:
        execute_line(code)
    except RuntimeError as e:
        print(f"Erro na linha {line_no}: {e}")
        # Em caso de erro, cancelamos o modo debug automaticamente
        stop_debug()
        return

    # Avança para próxima linha
    if idx + 1 < len(nums):
        program_counter = nums[idx + 1]
        print(f"[DEBUG] Próxima linha: {program_counter}")
    else:
        print("[DEBUG] Fim do programa alcançado.")
        stop_debug()


def show_stack() -> None:
    """
    Exibe o estado das variáveis do programa.
    Aqui usamos runtime_env como se fosse a 'pilha' de execução.
    """
    if not runtime_env:
        print("STACK vazia (nenhuma variável definida).")
        return
    print("STACK / Variáveis:")
    for k in sorted(runtime_env.keys()):
        print(f"  {k} = {runtime_env[k]!r}")


def stop_debug() -> None:
    """Sai do modo de depuração e reseta o program_counter."""
    global debug_mode, program_counter
    debug_mode = False
    program_counter = None
    print("Modo de depuração finalizado.")


# =====================================================================
# 6. LOOP PRINCIPAL (REPL)
# =====================================================================
# Responsável por:
# - Ler linha de comando do usuário,
# - Interpretar o comando (HELP, LOAD, LIST, INS, DEL, SAVE, RUN, DEBUG...),
# - Chamar as funções adequadas.
# É aqui que o usuário interage com o interpretador.
# =====================================================================


def parse_command(line: str) -> Tuple[str, str]:
    """
    Separa o comando (primeira palavra) e o resto como argumentos.
    Retorna (cmd_upper, args_str).
    """
    line = line.strip()
    if not line:
        return "", ""
    parts = line.split(maxsplit=1)
    cmd = parts[0].upper()
    args = parts[1] if len(parts) > 1 else ""
    return cmd, args


def main() -> None:
    """Loop principal do REPL: lê comandos e despacha para as funções."""
    global debug_mode

    print("MEPA/Lua – Interpretador em Python")
    print("Digite HELP para ajuda básica. EXIT para sair.\n")

    while True:
        try:
            # Prompt muda se estiver em modo debug
            prompt = "DEBUG> " if debug_mode else "> "
            line = input(prompt)
        except EOFError:
            print()
            break

        cmd, args = parse_command(line)
        if not cmd:
            continue

        # Comando de ajuda
        if cmd == "HELP":
            print("Comandos disponíveis:")
            print("  LOAD <arquivo>      - Carrega código numerado de um arquivo")
            print("  LIST                - Lista o programa em memória")
            print("  INS <linha> <cod>   - Insere/substitui linha")
            print("  DEL <linha>         - Remove linha")
            print("  DEL <li> <lf>       - Remove intervalo de linhas")
            print("  SAVE                - Salva programa em arquivo")
            print("  RUN                 - Executa programa inteiro")
            print("  DEBUG               - Entra em modo de depuração")
            print("  NEXT                - Executa próxima linha (modo DEBUG)")
            print("  STACK               - Mostra variáveis (modo DEBUG)")
            print("  STOP                - Sai do modo DEBUG")
            print("  EXIT                - Sai do programa")
            continue

        # Comando para sair do programa
        if cmd == "EXIT":
            if not ensure_can_discard_changes():
                # usuário quis salvar mas deu erro/cancelou
                continue
            print("Encerrando.")
            break

        # --------- comandos que funcionam tanto em debug quanto fora ----------
        if cmd == "LOAD":
            path = args.strip()
            if not path:
                print("Uso: LOAD <arquivo>")
            else:
                cmd_load(path)
            continue

        if cmd == "LIST":
            cmd_list()
            continue

        if cmd == "INS":
            if not args:
                print("Uso: INS <linha> <código>")
                continue
            parts = args.split(maxsplit=1)
            if len(parts) < 2:
                print("Uso: INS <linha> <código>")
                continue
            num_str, code = parts
            num = parse_int(num_str)
            if num is None or num < 0:
                print("Número de linha inválido.")
                continue
            cmd_ins(num, code)
            continue

        if cmd == "DEL":
            if not args:
                print("Uso: DEL <linha> ou DEL <linha_i> <linha_f>")
                continue
            parts = args.split()
            if len(parts) == 1:
                n = parse_int(parts[0])
                if n is None:
                    print("Número de linha inválido.")
                    continue
                cmd_del_single(n)
            elif len(parts) == 2:
                n1 = parse_int(parts[0])
                n2 = parse_int(parts[1])
                if n1 is None or n2 is None:
                    print("Números de linha inválidos.")
                    continue
                cmd_del_range(n1, n2)
            else:
                print("Uso: DEL <linha> ou DEL <linha_i> <linha_f>")
            continue

        if cmd == "SAVE":
            cmd_save()
            continue

        if cmd == "RUN":
            debug_mode = False
            run_sequential(debug=False)
            continue

        # ----------------- comandos específicos de DEBUG -----------------
        if cmd == "DEBUG":
            debug_mode = True
            run_sequential(debug=True)
            continue

        if cmd == "NEXT":
            if not debug_mode:
                print("NEXT só pode ser usado em modo DEBUG.")
                continue
            debug_next()
            continue

        if cmd == "STACK":
            if not debug_mode:
                print("STACK é útil em modo DEBUG (mas mostrando mesmo assim).")
            show_stack()
            continue

        if cmd == "STOP":
            if debug_mode:
                stop_debug()
            else:
                print("Não está em modo DEBUG.")
            continue

        # -----------------------------------------------------------------
        print(f"Comando desconhecido: {cmd}. Digite HELP para ajuda.")


if __name__ == "__main__":
    main()
