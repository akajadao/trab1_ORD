"""
Trabalho 1 - Organização e Recuperação de Dados

   Aluno: Jader Alves dos Santos
   RA: 120286
   
   Aluna: Janaina Maria Cera da Silva
   RA: 115832
   
   Aluno: Lucas Rodrigues Fedrigo
   RA: 129060
"""

from typing import List
from sys import argv
from readLed import readLed
from findRegister import findRegister
from removeRegister import removeRegister
from insertRegister import insertRegister
from defragFile import defragFile

def main() -> None:
    """Função principal que interpreta os argumentos de linha de comando e executa as operações."""
    if len(argv) < 2:
        print("Uso:")
        print("  python main.py -p <arquivo_binario>       # Para imprimir a LED")
        print("  python main.py -e <arquivo_binario> <arquivo_operacoes>      # Para realizar operações")
        print("  python main.py -c <arquivo_binario>       # Para compactar o arquivo_binario")
        return

    flag: str = argv[1]

    if flag == '-p':
        if len(argv) < 3:
            print("Erro: falta o nome do arquivo para imprimir a LED.")
            return
        file: str = argv[2]
        try:
            with open(file, 'r+b') as arq:
                cabecalho_bytes: bytes = arq.read(4)
                cabecalho: int = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
                readLed(arq, header=cabecalho)
        except FileNotFoundError:
            print("Arquivo não encontrado!")

    elif flag == '-e':
        if len(argv) < 4:
            print("Uso: -e <arquivo_dados> <arquivo_operacoes>")
            return
        file: str = argv[2]
        file_ops: str = argv[3]

        try:
            with open(file, 'r+b') as arq:
                cabecalho_bytes: bytes = arq.read(4)
                cabecalho: int = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)

                with open(file_ops, 'r', encoding='utf-8') as ops:
                    for linha in ops:
                        linha = linha.strip()
                        if not linha:
                            continue

                        op: str = linha[0]
                        dado: str = linha[2:]

                        if op == 'b':
                            id_busca: int = int(dado)
                            findRegister(arq, id_busca)
                            arq.seek(0)

                        elif op == 'i':
                            insertRegister(arq, dado)

                        elif op == 'r':
                            id_remover: int = int(dado)
                            removeRegister(arq, id_remover)

                        else:
                            print(f'Operação inválida na linha: {linha}')
                print(f'As operações do arquivo {file_ops} foram executadas com sucesso!')
        except FileNotFoundError:
            print('Arquivo não encontrado!')
        except UnicodeDecodeError:
            print(f'Erro: o arquivo {file_ops} precisa ser desfragmentado!')
    
    elif flag == '-c':
        if len(argv) < 3:
            print("Erro: falta o nome do arquivo para compactar.")
            return
        file: str = argv[2]
        try:
            with open(file, 'r+b') as arq:
                defragFile(arq)
            print(f'Arquivo desfragmentado com sucesso!')
        except FileNotFoundError:
            print("Arquivo não encontrado!")
    else:
        print(f"Flag desconhecida '{flag}'. Use '-p', '-e' ou '-c'.")

if __name__ == "__main__":
    main()
