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

def compactarArq(arq_file) -> None:
    """Função responsável pela remoção da fragmentação externa do arquivo binário.
    Remove apenas os registros marcados para remoção e não os registros que possuem algum tipo de fragmentação interna
    Reescreve o cabeçalho em -1 indicando que não há mais espaços disponíveis na LED."""
    with open('filmes.tmp', 'wb') as f:
        cab_int = -1
        cab = cab_int.to_bytes(4, byteorder='big', signed=True)
        f.write(cab)
        while True:
            tam, registro = leia_reg(arq_file, False, True)
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

def atualizaReg(arq, lista):
    """Função responsável pela ordenação interna da led best-fit, funciona da seguinte maneira:
    Compara lista1(offset, tamanho) com lista2(offset, tamanho) -> o tamanho menor é assumido como primeiro na led (em outras funções, não nessa) e aqui escrevemos no arquivo a ordenação com * nos espaços corretos"""
    for i, (offset, tamanho_atual) in enumerate(lista):
        arq.seek(offset)
        tam_bytes = arq.read(2)
        if len(tam_bytes) < 2:
            continue  # pula se falhar leitura

        tam = int.from_bytes(tam_bytes, byteorder='big', signed=False)
        buffer = arq.read(tam).decode(errors='ignore')

        id_base = buffer.split('*')[0].split('|')[0]  # garante que só o ID fique
        offset_maior = -1
        for j in range(i + 1, len(lista)):
            if lista[j][1] > tamanho_atual:
                offset_maior = lista[j][0]
                break
        resto = buffer.split('|', 1)[1] if '|' in buffer else ''
        novo_valor = f"{id_base}*{offset_maior}|".ljust(tam, '\0')

        arq.seek(offset + 2)
        arq.write(novo_valor.encode())

def remove_reg(arq, id_reg: int, hashmap_ids: dict, lista_led):
    """Função critica no nosso CRUD, retorna na variável lista_led qual item foi removido e offset, chamando atualizaReg para atualizar os ponteiros no arquivo, também atualiza o ponteiro no cabeçalho, de acordo com a lista"""
    print(f'Remoção do registro de chave "{id_reg}"')
    if id_reg not in hashmap_ids:
        print(f'Registro não encontrado!\n')
        return None

    offset = hashmap_ids[id_reg]
    arq.seek(offset)
    tam_bytes = arq.read(2)
    if len(tam_bytes) < 2:
        print(f'Erro ao ler tamanho do registro no offset {offset}\n')
        return None

    tam = int.from_bytes(tam_bytes, byteorder='big', signed=False)
    buffer = arq.read(tam).decode()

    campos = buffer.split('|')
    if not campos or len(campos[0]) == 0:
        print(f'Registro inválido ou vazio no offset {offset}\n')
        return None

    lista_led.append([offset, tam+2])
    lista_led.sort(key=lambda x: x[1])

    atualizaReg(arq, lista_led)

    # Atualiza o cabeçalho da LED
    arq.seek(0)
    novo_cab = lista_led[0][0].to_bytes(4, byteorder='big', signed=True)
    arq.write(novo_cab)
    hashmap_ids.pop(id_reg)
    print(f'Registro removido! ({tam} bytes)')
    print(f'Local: offset = {offset} bytes ({hex(offset)})\n')
    return True

def insertReg(arq, registro: str, hashmap_ids: dict = None, lista_led = None):
    """Função que escreve os registros, para registros com espaço suficiente em um item da LED, é feita a comparação de tamanhos, o menor espaço suficiente encontrado será o escolhido, caso contrário, vai para o final do arquivo.
    Também chama atualizaReg para atualizar os novos ponteiros disponíveis, removendo o ponteiro atual."""
    print(f'Inserção do registro de chave "{registro.split('|')[0]}" ({len(registro)+1} bytes)')
    if int(registro.split('|')[0]) in hashmap_ids:
        print('Erro: já existe um registro com essa chave.\n')
        return None

    pos_atual = arq.tell()
    arq.seek(0)
    cab_bytes = arq.read(4)
    cab = int.from_bytes(cab_bytes, byteorder='big', signed=True)  # offset do primeiro removido

    campos = registro.strip('|').split('|')
    if len(campos) < 7:
        raise ValueError("Registro incompleto. Esperado 7 campos.\n")

    id_reg = int(campos[0])
    registro_bytes = registro.encode()
    tam_novo = len(registro_bytes)

    # Se LED está vazia, insere no final
    if cab == -1:
        arq.seek(0, 2)
        offset = arq.tell()
        arq.write(tam_novo.to_bytes(2, 'big', signed=False))
        arq.write(registro_bytes)
        hashmap_ids[id_reg] = offset
        print(f'Local: fim do arquivo\n')
        arq.seek(pos_atual)
        return None

    # Melhor ajuste
    melhor_offset = None
    melhor_tam = None
    melhor_prox = None
    anterior_offset = None
    anterior_led = None

    atual_offset = cab
    while atual_offset != -1:
        arq.seek(atual_offset)
        tam_bytes = arq.read(2)
        if len(tam_bytes) < 2:
            break

        tam_disp = int.from_bytes(tam_bytes, 'big',signed=False)
        buffer = arq.read(tam_disp)

        try:
            conteudo = buffer.decode()
            id_info = conteudo.split('|')[0]
            prox_led = int(id_info.split('*')[1])
        except:
            break

        if tam_disp >= tam_novo:
            if melhor_tam is None or tam_disp < melhor_tam:
                melhor_offset = atual_offset
                melhor_tam = tam_disp
                melhor_prox = prox_led
                anterior_led = anterior_offset

        anterior_offset = atual_offset
        atual_offset = prox_led

    if melhor_offset is not None:
        # Reaproveita o melhor espaço encontrado
        arq.seek(melhor_offset)
        arq.write(melhor_tam.to_bytes(2, 'big', signed=False))
        arq.write(registro_bytes)

        # Preenche com \0 os bytes restantes, se houver
        sobra = melhor_tam - tam_novo
        if sobra > 0:
            arq.write(b'\0' * sobra)

        if melhor_offset == cab:
            # atualizou o primeiro nó da LED, atualiza cabeçalho
            arq.seek(0)
            arq.write(melhor_prox.to_bytes(4, 'big', signed=True))
        else:
            # atualizou um nó intermediário da LED: atualiza ponteiro do anterior
            arq.seek(anterior_led)
            arq.read(2)  # pula tamanho
            buffer = arq.read(10)  # leitura segura
            partes = buffer.decode(errors='ignore').split('|')[0].split('*')
            if len(partes) == 2:
                novo_id = f"{partes[0]}*{melhor_prox}".ljust(len(partes[0]) + len(partes[1]) + 1)
                novo_led = f"{novo_id}|".encode()
                arq.seek(anterior_led + 2)
                arq.write(novo_led)

        hashmap_ids[id_reg] = melhor_offset
        print(f'Local: offset = {melhor_offset} bytes ({hex(melhor_offset)})\n')

    else:
        arq.seek(0, 2)
        offset = arq.tell()
        arq.write(tam_novo.to_bytes(2, 'big'))
        arq.write(registro_bytes)
        hashmap_ids[id_reg] = offset
        print(f'Local: fim do arquivo\n')

    if lista_led:
        lista_led[:] = [item for item in lista_led if item[0] != melhor_offset]
    atualizaReg(arq, lista_led)

    arq.seek(pos_atual)

def leia_reg(file, com_offset: bool = False, compactar: bool = False) -> tuple | str | None:
    """ o famoso leia registros, porém com novas funcionalidades, agora também retorna ponteiro e o tamanho do registro, para caso eu queira compactar/atualizar minha LED na memória"""
    offset = file.tell()
    tam_reg = file.read(2)
    if len(tam_reg) < 2:
        if com_offset:
            return None, None
        if compactar:
            return -1, None
        else:
            return None

    tam = int.from_bytes(tam_reg, byteorder='big', signed=False)

    if tam > 0:
        buffer = file.read(tam)
        buffer = buffer.decode()
        if com_offset:
            return offset, buffer
        elif compactar:
            return tam_reg, buffer
        else:
            return buffer
    else:
        if com_offset:
            return offset, ''
        if compactar:
            return -1, ''
        return ''

def buscaId(file, id_reg: int, hashmap_ids: dict) -> str | bool:
    """Faz um query nos ids via hashmap montado, isso reduz o custo de memória imensamente."""
    try:
        print(f'Busca pelo registro de chave "{id_reg}"')
        if id_reg not in hashmap_ids:
            print(f'Erro: registro não encontrado.\n')
            return None

        offset = hashmap_ids[id_reg]
        file.seek(offset)
        tam, reg = leia_reg(file, False, True)
        reg += f' ({int.from_bytes(tam, byteorder='big', signed=False)} bytes)\nLocal: offset = {offset} bytes ({hex(offset)})\n'
        print(reg)
        return True
    except (ValueError, FileNotFoundError) as e:
        return f'Erro: {e}'

def monta_hashmap(arq_file) -> dict:
    """Como diz o nome da função, cria um hashmap formatado em dict(id, offset) e também um outro como uma lista[offset, tamanho], lista_led só atualiza caso encontre um ponteiro no id do registro *, e também via atualizaReg"""
    hashmap_ids = {}
    lista_led = []
    while True:
        offset, registro = leia_reg(arq_file, True)
        if offset is None:
            break

        if not registro or '|' not in registro:
            continue  # ignora registros vazios ou inválidos

        partes = registro.split('|')
        id_campo = partes[0]

        if not id_campo.strip():  # ignora se o ID estiver vazio
            continue

        if '*' in str(id_campo):
            lista_led.append([offset, len(registro)+2])  # registro removido (está na LED)
        else:
            try:
                id_reg = int(id_campo)
                hashmap_ids[id_reg] = offset
            except ValueError:
                print(f"ID inválido no offset {offset}: {registro}")
    return hashmap_ids, lista_led

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
                tam_bytes = arq.read(2)
                if len(tam_bytes) < 2:
                    break
                
                tam = int.from_bytes(tam_bytes, 'big')

                buffer = arq.read(tam)
                try:
                    registro = buffer.decode()
                    id_campo = registro.split('|')[0]
                    prox = int(id_campo.split('*')[1])
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
                #print(f'Cabeçalho: {cabecalho}')
                hashmap, lista_led = monta_hashmap(arq)
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
                            buscaId(arq, id_busca, hashmap)

                        elif op == 'i':
                            # insere registro
                            registro = dado
                            insertReg(arq, registro, hashmap, lista_led)

                        elif op == 'r':
                            # remove registro
                            id_remover = int(dado)
                            remove_reg(arq, id_remover, hashmap, lista_led)

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