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

def updateLED(arq, offset_reg, tam_reg, isRemove=True):
    first = True
    arq.seek(0)
    cab = arq.read(4)
    cabecalho = int.from_bytes(cab, 'big', signed=True)
    if isRemove:
        if cabecalho == -1:
            arq.seek(0)
            offset_led = offset_reg.to_bytes(4, 'big', signed=True)
            arq.write(offset_led)
            arq.seek(offset_reg)
            reg_led = b'*'+(-1).to_bytes(4, 'big', signed=True)
            arq.write(tam_reg.to_bytes(2, 'big', signed=False))
            arq.write(reg_led)
            return
        else:
            arq.seek(cabecalho)
            dados = readReg(arq, isTam=True, isOffset=True)
            old_reg, old_tam, old_offset = dados
            while True:
                if old_tam > tam_reg:
                    arq.seek(offset_reg)
                    reg_led = b'*'+old_offset.to_bytes(4, 'big', signed=True)
                    arq.write(tam_reg.to_bytes(2, 'big', signed=False))
                    arq.write(reg_led)
                    if first == True:
                        arq.seek(0)
                        arq.write(offset_reg.to_bytes(4,'big', signed=True))
                        ## escreveu no topo
                        return
                    first = False                    
                    return
                if old_tam < tam_reg:
                    arq.seek(old_offset)
                    arq.write(old_tam.to_bytes(2,'big',signed=False))
                    old_led = b'*'+offset_reg.to_bytes(4, 'big', signed=True)
                    arq.write(old_led)
                    arq.seek(offset_reg)
                    if (old_reg == -1) and (first == True):
                        arq.write(tam_reg.to_bytes(2, 'big', signed=False))
                        reg_led = b'*'+(-1).to_bytes(4,'big', signed=True)
                        arq.write(reg_led)
                        return
                first = False
                count += 1
                dados = readReg(arq, isTam=True,isOffset=True)
                old_reg, old_tam, old_offset = dados
            
def insereNaLEDBestFit(arq, offset_removido, tam_removido, cabecalho):
    """
    Insere o espaço removido na LED usando a estratégia Best Fit.
    Atualiza os ponteiros da lista encadeada de espaços disponíveis.
    """
    arq.seek(0)
    if cabecalho == -1:
        # LED vazia
        arq.write(offset_removido.to_bytes(4, 'big', signed=True))
        arq.seek(offset_removido)
        reg_led = b'*'+ (-1).to_bytes(4, 'big', signed=True)  # ponteiro para próximo
        arq.write(tam_removido.to_bytes(2, 'big'))
        arq.write(reg_led)
        return

    # Busca Best Fit
    offset_atual = cabecalho
    offset_anterior = None
    melhor_offset = None
    melhor_tam = None
    melhor_anterior = None

    while offset_atual != -1:
        arq.seek(offset_atual)
        tam_bytes = arq.read(2)
        tam_led = int.from_bytes(tam_bytes, 'big', signed=False)
        marcador = arq.read(1)
        ponteiro_prox = int.from_bytes(arq.read(4), 'big', signed=True)

        if tam_led >= tam_removido:
            if melhor_tam is None or tam_led < melhor_tam:
                melhor_offset = offset_atual
                melhor_tam = tam_led
                melhor_anterior = offset_anterior

        offset_anterior = offset_atual
        offset_atual = ponteiro_prox

    # Inserção ordenada
    if melhor_anterior is None:
        # Inserir no topo da LED
        arq.seek(offset_removido)
        arq.write(tam_removido.to_bytes(2, 'big', signed=False))
        arq.write(b'*')
        arq.write(cabecalho.to_bytes(4, 'big', signed=True))

        # Atualiza cabeçalho
        arq.seek(0)
        arq.write(offset_removido.to_bytes(4, 'big', signed=True))
    else:
        # Inserir após melhor_anterior e antes de melhor_offset
        arq.seek(melhor_anterior + 2 + 1)  # após tam e '*'
        arq.write(offset_removido.to_bytes(4, 'big', signed=True))

        arq.seek(offset_removido)
        arq.write(tam_removido.to_bytes(2, 'big'))
        arq.write(b'*')
        prox = melhor_offset if melhor_offset is not None else -1
        arq.write(prox.to_bytes(4, 'big', signed=True))

def recursivaInsert(arq, tam, offset, registro):
    arq.seek(offset)
    new_offset, tam_led = readReg(arq, isTam=True)

    if tam_led >= tam:
        tam_bytes = int.to_bytes(tam_led, 2, 'big', signed=False)
        registro_bytes = registro.encode().ljust(tam_led, b'\0')
        arq.seek(offset)
        arq.write(tam_bytes)
        arq.write(registro_bytes)
        print(f'Local: offset = {offset} bytes ({hex(offset)})\n')
        return

    if new_offset != -1:
        recursivaInsert(arq, tam, new_offset, registro)
    else:
        arq.seek(0, 2)  # Fim do arquivo
        tam_bytes = int.to_bytes(tam, 2, 'big', signed=False)
        registro_bytes = registro.encode().ljust(tam, b'\0')
        arq.write(tam_bytes)
        arq.write(registro_bytes)
        print(f'Local: fim do arquivo\n')
        return

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
            updateLED(arq, offset, tam)
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
        recursivaInsert(arq, tam, cab, registro)

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
        if reg.startswith('*'):
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