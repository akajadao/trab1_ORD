"""
Trabalho 1 - Organização e Recuperação de Dados

   Aluno: Jader Alves dos Santos
   RA: 120286
   
   Aluna: Janaina Maria Cera da Silva
   RA: 115832
   
   Aluno: Lucas Rodrigues Fedrigo
   RA: 129060
"""

from sys import argv
from readLed import readLed
from findRegister import findRegister
from removeRegister import removeRegister
from insertRegister import insertRegister
from defragFile import defragFile


def main():
    """Apenas a função main, que chama as outras funções."""
    if len(argv) < 2:
        print("Uso:")
        print("  python led.py -p <arquivo>       # Para imprimir a LED")
        print("  python led.py -e <arquivo>       # Para realizar operações")
        print("  python led.py -c <arquivo>       # Para compactar o arquivo")
        return

    flag = argv[1]

    if flag == '-p':
        if len(argv) < 3:
            print("Erro: falta o nome do arquivo para imprimir a LED.")
            return
        arquivo = argv[2]
        try:
            with open(arquivo, 'r+b') as arq:
                cabecalho_bytes = arq.read(4)
                cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
                readLed(arq, header=cabecalho)
        except FileNotFoundError: 'Arquivo não encontrado!'

    elif flag == '-e':
        if len(argv) < 4:
            print("Uso: -e <arquivo_dados> <arquivo_operacoes>")
            return
        arquivo = argv[2]
        arquivo_ops = argv[3]

        try:
            with open(arquivo, 'r+b') as arq:
                cabecalho_bytes = arq.read(4)
                cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
                with open(arquivo_ops, 'r', encoding='utf-8') as ops:
                    for linha in ops:
                        linha = linha.strip()
                        if not linha:
                            continue
                        op = linha[0]
                        dado = linha[2:]

                        if op == 'b':
                            # busca id
                            id_busca = int(dado)
                            findRegister(arq, id_busca)
                            arq.seek(0)

                        elif op == 'i':
                            # insere registro
                            registro = dado
                            insertRegister(arq, registro)

                        elif op == 'r':
                            # remove registro
                            id_remover = int(dado)
                            removeRegister(arq, id_remover)

                        else:
                            print(f'Operação inválida na linha: {linha}')
                    print(f'As operações do arquivo {argv[1]}/{argv[2]} foram executadas com sucesso!')
        except FileNotFoundError:
            print('Arquivo não encontrado!')
        except UnicodeDecodeError:
            print(f'Erro: o arquivo {argv[2]} precisa ser desfragmentado!')
    elif flag == '-c':
        arquivo = argv[2]
        with open(arquivo, 'r+b') as arq:
            defragFile(arq)
        print(f'Arquivo desfragmentado com sucesso!')
    else:
        print(f"Flag desconhecida '{flag}'. Use '-p' para imprimir a LED ou '-e' para abrir arquivo.")

if __name__ == "__main__":
    main()