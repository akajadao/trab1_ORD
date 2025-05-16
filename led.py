"""Trabalho de ORD
Alunos:
Jader Alves dos Santos - RA120286
Janaina Maria Cera da Silva - RA115832
Lucas Rodrigues Fedrigo - RA129060"""

def remove_reg(arq, cabecalho: str, id_reg: int, hashmap_ids: dict):
    if id_reg not in hashmap_ids:
        print(f'Registro não encontrado!')
        return None

    offset = hashmap_ids[id_reg]
    arq.seek(offset)
    tam_bytes = arq.read(2)
    if len(tam_bytes) < 2:
        print(f'Erro ao ler tamanho do registro no offset {offset}')
        return None

    tam = int.from_bytes(tam_bytes, byteorder='big', signed=False)
    buffer = arq.read(tam).decode()

    campos = buffer.split('|')
    if not campos or len(campos[0]) == 0:
        print(f'Registro inválido ou vazio no offset {offset}')
        return None

    # Substitui apenas o primeiro campo (ID) por "ID*cabecalho"
    campos[0] = f"{id_reg}*{cabecalho}"
    novo_reg = '|'.join(campos)
    novo_reg_bytes = novo_reg.encode()

    arq.seek(offset)
    arq.write(tam_bytes)  # reescreve o tamanho
    arq.write(novo_reg_bytes)

    # Atualiza o cabeçalho da LED
    arq.seek(0)
    novo_cab = offset.to_bytes(4, byteorder='big', signed=True)
    arq.write(novo_cab)

    print(f'Remoção do registro de chave "{id_reg}"')
    print(f'Registro removido! ({tam} bytes)')
    print(f'Local: offset = {offset} bytes ({hex(offset)})')
    return True


def escreve_reg(arq, registro: str, hashmap_ids: dict = None):
    if hashmap_ids is None:
        hashmap_ids = {}

    pos_atual = arq.tell()
    arq.seek(0)
    cab_bytes = arq.read(4)
    cab = int.from_bytes(cab_bytes, byteorder='big', signed=True)  # offset do primeiro removido

    campos = registro.strip('|').split('|')
    if len(campos) < 7:
        raise ValueError("Registro incompleto. Esperado 7 campos.")

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
        print(f'Registro inserido no final: {registro}\nOffset: {offset}')
        arq.seek(pos_atual)
        return

    # Melhor ajuste
    melhor_offset = None
    melhor_tam = None
    melhor_prox = None
    anterior_offset = None
    anterior_prox = None

    atual_offset = cab
    while atual_offset != -1:
        arq.seek(atual_offset)
        tam_bytes = arq.read(2)
        if len(tam_bytes) < 2:
            break

        tam_disp = int.from_bytes(tam_bytes, 'big')
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
                anterior_prox = atual_offset  # atual é próximo do anterior

        # Continua LED
        anterior_offset = atual_offset
        atual_offset = prox_led

    if melhor_offset is not None:
        # Reaproveita o melhor espaço encontrado
        arq.seek(melhor_offset)
        arq.write(tam_novo.to_bytes(2, 'big'))
        arq.write(registro_bytes)
        hashmap_ids[id_reg] = melhor_offset
        print(f'Registro reaproveitou espaço (melhor ajuste): {registro}\nOffset: {melhor_offset}')

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
                novo_id = f"{partes[0]}*{melhor_prox}".ljust(len(partes[0])+len(partes[1])+1)
                novo_led = f"{novo_id}|".encode()
                arq.seek(anterior_led + 2)
                arq.write(novo_led)
    else:
        # Insere no final
        arq.seek(0, 2)
        offset = arq.tell()
        arq.write(tam_novo.to_bytes(2, 'big'))
        arq.write(registro_bytes)
        hashmap_ids[id_reg] = offset
        print(f'Registro inserido no final (sem espaço adequado): {registro}\nOffset: {offset}')

    arq.seek(pos_atual)

def insertReg(arq, registro: str, hashmap_ids: dict) -> None:
    try:
        escreve_reg(arq, registro, hashmap_ids)
    except Exception as e:
        print(f'Erro ao inserir registro: {e}')

def leia_reg(file, com_offset: bool = False) -> tuple | str | None:
    offset = file.tell()
    tam_reg = file.read(2)
    if len(tam_reg) < 2:
        return (None, None) if com_offset else None

    tam = int.from_bytes(tam_reg, byteorder='big', signed=False)

    if tam > 0:
        buffer = file.read(tam)
        buffer = buffer.decode()
        return (offset, buffer) if com_offset else buffer
    else:
        return (offset, '') if com_offset else ''

def buscaId(file, id_reg: int, hashmap_ids: dict) -> str:
    try:
        if id_reg not in hashmap_ids:
            return f'Erro: registro não encontrado.'

        offset = hashmap_ids[id_reg]
        file.seek(offset)
        reg = leia_reg(file)
        reg += f' ({len(reg)+2} bytes)\nLocal: offset = {offset} bytes ({hex(offset)})'
        return reg
    except (ValueError, FileNotFoundError) as e:
        return f'Erro: {e}'

def monta_hashmap(arq: str) -> dict:
    hashmap_ids = {}

    with open(arq, 'rb') as f:
        f.read(4)  # pula o cabeçalho da LED

        while True:
            offset, registro = leia_reg(f, True)
            if offset is None:
                break

            if not registro or '|' not in registro:
                continue  # ignora registros vazios ou inválidos

            partes = registro.split('|')
            id_campo = partes[0]

            if not id_campo.strip():  # ignora se o ID estiver vazio
                continue

            if '*' in id_campo:
                continue  # registro removido (está na LED)
            else:
                try:
                    id_reg = int(id_campo)
                    hashmap_ids[id_reg] = offset
                except ValueError:
                    print(f"ID inválido no offset {offset}: {registro}")

    return hashmap_ids


def main(arquivo: str):
    try:
        hashmap = monta_hashmap(arquivo)
        with open(arquivo, 'r+b') as arq:
            cabecalho_bytes = arq.read(4)
            cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
            print(f'Cabeçalho: {cabecalho}')
            #resultado = buscaId(arq, 113, hashmap)
            #print(resultado)

            #novo_registro = '66|500 Dias com Ela|Marc Webb|2009|Comédia, Drama, Romance|95|Joseph Gordon|'
            #insertReg(arq, novo_registro, hashmap)
            #remove_reg(arq, cabecalho, 66, hashmap)

    except FileNotFoundError:
        print('Arquivo não encontrado!')

if __name__ == '__main__':
    main('filmes.dat')
