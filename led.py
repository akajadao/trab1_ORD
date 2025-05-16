"""Trabalho de ORD
Alunos:
Jader Alves dos Santos - RA120286
Janaina Maria Cera da Silva - RA115832
Lucas Rodrigues Fedrigo - RA129060"""

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
            return f'ID {id_reg} não encontrado.'

        offset = hashmap_ids[id_reg]
        file.seek(offset)
        reg = leia_reg(file)
        return reg
    except (ValueError, FileNotFoundError) as e:
        return f'Erro: {e}'

def monta_hashmap(arq: str) -> dict:
    hashmap_ids = {}

    with open(arq, 'rb') as f:
        f.read(4)  # pula o cabeçalho de 4 bytes

        while True:
            offset, registro = leia_reg(f, True)
            if offset is None:
                break
            if registro:
                partes = registro.split('|')
                try:
                    id_reg = int(partes[0])
                    hashmap_ids[id_reg] = offset
                except ValueError:
                    print(f"ID inválido no offset {offset}: {registro}")

    return hashmap_ids

def main(arquivo: str):
    try:
        hashmap_ids: dict = monta_hashmap(arquivo)
        with open(arquivo, 'rb') as arq:
            cabecalho_bytes = arq.read(4)
            cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
            print(f'Cabeçalho: {cabecalho}')
            resultado = buscaId(arq, 113, hashmap_ids)
            print(resultado)

    except FileNotFoundError:
        print('Arquivo não encontrado!')



if __name__ == '__main__':
    main('filmes.dat')