"""Trabalho de ORD
Alunos:
Jader Alves dos Santos - RA120286
Janaina Maria Cera da Silva - RA115832
Lucas Rodrigues Fedrigo - RA129060

'LED best-fit: menor espaço -> maior espaço'

O sistema compõe de dois hashmaps de responsáveis pela organização em memória dos dados do arquivo, e após cada operação
as alterações são salvas no arquivo em si.
"""

import sys
import os

def updateLED(arq, offset_reg=0, tam_reg=0, buffer_reg=0, isRemove=False, isInsert=False):
    arq.seek(0)
    cabecalho = int.from_bytes(arq.read(4), 'big', signed=True)

    if isRemove:
        if cabecalho == -1:
            # LED vazia, insere novo como cabeça
            arq.seek(0)
            arq.write(offset_reg.to_bytes(4, 'big', signed=True))
            arq.seek(offset_reg)
            arq.write(tam_reg.to_bytes(2, 'big', signed=False))
            arq.write(b'*' + (-1).to_bytes(4, 'big', signed=True))
            return
        else:
            # Percorre LED até encontrar ponto de inserção
            prev_offset = None
            current_offset = cabecalho

            while current_offset != -1:
                arq.seek(current_offset)
                tam_atual = int.from_bytes(arq.read(2), 'big', signed=False)
                marcador = arq.read(1)  # Deve ser b'*'
                prox_offset = int.from_bytes(arq.read(4), 'big', signed=True)

                if tam_reg < tam_atual:
                    # Inserir antes do current_offset
                    arq.seek(offset_reg)
                    arq.write(tam_reg.to_bytes(2, 'big', signed=False))
                    arq.write(b'*' + current_offset.to_bytes(4, 'big', signed=True))

                    if prev_offset is None:
                        # Inserção no topo
                        arq.seek(0)
                        arq.write(offset_reg.to_bytes(4, 'big', signed=True))
                    else:
                        # Atualiza ponteiro do anterior
                        arq.seek(prev_offset + 2 + 1)  # 2 bytes do tam + 1 do '*'
                        arq.write(offset_reg.to_bytes(4, 'big', signed=True))
                    return

                prev_offset = current_offset
                current_offset = prox_offset

            # Chegou ao fim, insere no final
            arq.seek(offset_reg)
            arq.write(tam_reg.to_bytes(2, 'big', signed=False))
            arq.write(b'*' + (-1).to_bytes(4, 'big', signed=True))

            if prev_offset is not None:
                arq.seek(prev_offset + 2 + 1)
                arq.write(offset_reg.to_bytes(4, 'big', signed=True))
                return
    if isInsert:
            arq.seek(cabecalho)
            dados = readReg(arq, isTam=True, isOffset=True)
            old_reg, old_tam, old_offset = dados
            print(old_reg)
            if old_reg == -1:
                if old_tam > (tam_reg):
                    arq.seek(old_offset)
                    arq.write(old_tam.to_bytes(2, 'big', signed=False))
                    buffer = buffer_reg.ljust(old_tam, '\0')
                    arq.write(buffer.encode())
                    print(f'Local: offset = {old_offset} bytes ({hex(old_offset)})\n')
                    arq.seek(0)
                    arq.write((-1).to_bytes(4, 'big', signed=True))
                    return
                else:
                    arq.seek(0, 2)                    
                    arq.write(tam_reg.to_bytes(2), 'big', signed=False)
                    buffer = buffer_reg.encode()
                    arq.write(buffer)
                    print('Local: fim do arquivo\n')
                    return
            else:
                while True:
                    print(old_reg)
                    arq.seek(old_reg)
                    new_dados = readReg(arq, isTam=True, isOffset=True)
                    new_reg, new_tam, new_offset = new_dados
                    if new_reg == -1:
                        if new_tam > (tam_reg):
                            arq.seek(old_reg)
                            arq.write(new_tam.to_bytes(2, 'big', signed=False))
                            buffer = buffer_reg.ljust(new_tam, '\0')
                            arq.write(buffer.encode())
                            print(f'Local: offset = {new_offset} bytes ({hex(new_offset)})')
                            arq.seek(old_offset)
                            arq.write(old_tam.to_bytes(2, 'big', signed=False))
                            arq.write(b'*'+(-1).to_bytes(4, 'big', signed=True))
                            return
                        else:
                            arq.seek(0,2)
                            arq.write(tam_reg.to_bytes(2, 'big', signed=False))
                            arq.write(buffer_reg.encode())
                            print('Local: fim do arquivo')
                            return
                    else:
                        if new_tam > (tam_reg):
                            arq.seek(old_reg)
                            arq.write(new_tam.to_bytes(2, 'big', signed=False))
                            buffer = buffer_reg.ljust(new_tam, '\0')
                            arq.write(buffer.encode())
                            print(f'Local: offset = {new_offset} bytes ({hex(new_offset)})')
                            arq.seek(old_offset)
                            arq.write(old_tam.to_bytes(2, 'big', signed=False))
                            arq.write(b'*'+new_reg.to_bytes(4, 'big', signed=True))
                            return
                        else:
                            old_reg, old_tam, old_offset = new_reg, new_tam, new_offset

def compactarArq(arq_file) -> None:
    """Função responsável pela remoção da fragmentação externa do arquivo binário.
    Remove apenas os registros marcados para remoção e não os registros que possuem algum tipo de fragmentação interna
    Reescreve o cabeçalho em -1 indicando que não há mais espaços disponíveis na LED."""
    with open('filmes.tmp', 'wb') as f:
        cab_int = -1
        cab = cab_int.to_bytes(4, byteorder='big', signed=True)
        f.write(cab)
        while True:
            tam, registro = readReg(arq_file, False, True)
            if tam == -1:
                break
            
            if not registro or '|' not in registro:
                continue  # ignora registros vazios ou inválidos
            
            partes = registro.split('|')
            id_campo = partes[0]
    
            if not id_campo.strip():  # ignora se o ID estiver vazio
                continue
            
            if '*' in str(id_campo):
                continue
            else:
                try:
                    f.write(tam)
                    registro = registro.encode()
                    f.write(registro)
                except ValueError:
                    print(f"Tamanho inválido {int.from_bytes(tam, 'big', False)}: {registro}")
        print(f'O arquivo {sys.argv[2]} foi compactado com sucesso!')
        return None

def removeReg(arq, id_reg):
    """Remove logicamente um registro pelo id_reg e atualiza a LED no arquivo usando Best Fit."""
    print(f'Remoção do registro de chave "{id_reg}"')
    arq.seek(0)
    arq.read(4)

    while True:
        dados = readReg(arq, isTam=True, isOffset=True)
        if not dados:
            break
        reg, tam, offset = dados
        if isinstance(reg, int):
            continue
        campos = reg.split('|')
        if int(campos[0]) == int(id_reg):
            # Marcar como removido, mantendo os dados antigos
            updateLED(arq, offset, tam, reg, isRemove = True)
            print(f'Registro removido! ({tam} bytes)')
            print(f'Local: offset = {offset} bytes ({hex(offset)})\n')
            return offset, tam
    print(f'Registro não encontrado!\n')
    return None

def insertReg(arq, registro: str, cab: int):
    """Função que escreve os registros, para registros com espaço suficiente em um item da LED, é feita a comparação de tamanhos, o menor espaço suficiente encontrado será o escolhido, caso contrário, vai para o final do arquivo."""
    print(f'Inserção do registro de chave "{registro.split('|')[0]}" ({len(registro)+2} bytes)')
    tam = len(registro)
    if cab == -1:
        arq.seek(0,2)
        tam_bytes = int.to_bytes(tam, 2, 'big', signed=False)
        registro_bytes = registro.encode()
        arq.write(tam_bytes)
        arq.write(registro_bytes)
        print(f'Local: fim do arquivo\n')
    else:
        updateLED(arq, offset_reg=0, tam_reg=tam, buffer_reg=registro, isInsert=True)

def readReg(arq, isTam=False, isOffset=False):
    """
    Lê um registro do arquivo e retorna, conforme os parâmetros:
    - o buffer do conteúdo
    - o tamanho (em bytes)
    - o offset no arquivo
    Se o registro estiver marcado como removido (começa com '*'), retorna o ponteiro LED.
    """
    pos = arq.tell()
    tam_bytes = arq.read(2)
    
    if len(tam_bytes) < 2:
        return None

    tam = int.from_bytes(tam_bytes, 'big', signed=False)

    if tam == 0:
        return None  # registro vazio ou inválido

    buffer = arq.read(tam)
    if len(buffer) < tam:
        return None  # erro de leitura

    if buffer.startswith(b'*'):
        # Registro marcado como removido
        conteudo_bytes = buffer[1:5]
        conteudo = int.from_bytes(conteudo_bytes, 'big', signed=True)
        if isTam and isOffset:
            return conteudo, tam, pos
        if isTam:
            return conteudo, tam
        if isOffset:
            return conteudo, pos
        else:
            return conteudo
    else:
        # Registro ativo
        conteudo = buffer.decode(errors='ignore')
        if isTam and isOffset:
            return conteudo, tam, pos
        if isTam:
            return conteudo, tam
        if isOffset:
            return conteudo, pos
        else:
            return conteudo
    return None

def buscaId(arq, id_reg):
    """Percorre o arquivo buscando um registro com o ID especificado."""
    print(f'Busca pelo registro de chave "{id_reg}"')
    arq.seek(4)  # Pula o cabeçalho da LED (4 bytes)

    while True:
        dados = readReg(arq, isTam=True, isOffset=True)
        if not dados:
            break  # Fim do arquivo

        reg, tam, offset = dados

        # Ignora registros removidos logicamente (marcados com '*')
        if isinstance(reg, int):
            continue

        campos = reg.split('|')
        if int(campos[0]) == int(id_reg):
            reg += f' ({tam} bytes)\nLocal: offset = {offset} bytes ({hex(offset)})\n'
            print(reg)
            return reg, tam, offset
    print('Erro: registro não encontrado.\n')
    return None

def imprime_led(arquivo):
    """Só realmente faz a impressão da LED pelo offset apontado nos registros."""
    try:
        with open(arquivo, 'rb') as arq:
            arq.seek(0)
            cabecalho_bytes = arq.read(4)
            cab = int.from_bytes(cabecalho_bytes, 'big', signed=True)

            if cab == -1:
                print("LED -> fim")
                print("Total: 0 espaços disponíveis")
                print("A LED foi impressa com sucesso!")
                return

            total = 0
            output = "LED"

            while cab != -1:
                arq.seek(cab)
                dados = readReg(arq, isTam=True)
                buffer, tam = dados
                if buffer == None:
                    break
                try:
                    prox = int(buffer)
                except Exception as e:
                    print(e)
                    break

                output += f" -> [offset: {cab}, tam: {tam}]"
                total += 1
                cab = prox
            

            output += " -> fim"
            print(output)
            print(f"Total: {total} espaços disponíveis")
            print("A LED foi impressa com sucesso!")

    except FileNotFoundError:
        print("Arquivo não encontrado!")
    except Exception as e:
        print(f"Erro ao imprimir LED: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python led.py -p <arquivo>       # Para imprimir a LED")
        print("  python led.py -e <arquivo>       # Para realizar operações")
        print("  python led.py -c <arquivo>       # Para compactar o arquivo")
        return

    flag = sys.argv[1]

    if flag == '-p':
        if len(sys.argv) < 3:
            print("Erro: falta o nome do arquivo para imprimir a LED.")
            return
        arquivo = sys.argv[2]
        imprime_led(arquivo)

    elif flag == '-e':
        if len(sys.argv) < 4:
            print("Uso: -e <arquivo_dados> <arquivo_operacoes>")
            return
        arquivo = sys.argv[2]
        arquivo_ops = sys.argv[3]

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
                            buscaId(arq, id_busca)
                            arq.seek(0)

                        elif op == 'i':
                            # insere registro
                            arq.seek(0)
                            cabecalho_bytes = arq.read(4)
                            cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
                            registro = dado
                            insertReg(arq, registro, cabecalho)

                        elif op == 'r':
                            # remove registro
                            id_remover = int(dado)
                            removeReg(arq, id_remover)

                        else:
                            print(f'Operação inválida na linha: {linha}')
                    print(f'As operações do arquivo {sys.argv[1]}/{sys.argv[2]} foram executadas com sucesso!')
        except FileNotFoundError:
            print('Arquivo não encontrado!')
        except UnicodeDecodeError:
            print(f'Erro: o arquivo {sys.argv[2]} precisa ser desfragmentado!')
    elif flag == '-c':
        arquivo = sys.argv[2]
        with open(arquivo, 'r+b') as arq:
            cabecalho_bytes = arq.read(4)
            cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
            compactarArq(arq)
        os.replace('filmes.tmp', sys.argv[2])
        print(f'Renomeado com sucesso!')
    else:
        print(f"Flag desconhecida '{flag}'. Use '-p' para imprimir a LED ou '-e' para abrir arquivo.")

if __name__ == '__main__':
    main()