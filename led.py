"""Trabalho de ORD
Alunos:
Jader Alves dos Santos - RA120286
Janaina Maria Cera da Silva - RA115832
Lucas Rodrigues Fedrigo - RA129060"""

def remove_reg(id_reg, hashmap_id: dict):
    offset = hashmap_id[id_reg]

def escreve_reg(arq, registro: str, hashmap_ids: dict = None):
    if hashmap_ids is None:
        hashmap_ids = {}

    pos_atual = arq.tell()
    arq.seek(0)
    cab_bytes = arq.read(4)
    cab = int.from_bytes(cab_bytes, byteorder='big', signed=True)

    if cab == -1:
        arq.seek(0, 2)  # vai para o final do arquivo

        campos = registro.strip('|').split('|')
        if len(campos) < 7:
            raise ValueError("Registro incompleto. Esperado 7 campos.")

        offset = arq.tell()
        registro_bytes = registro.encode()
        tam = len(registro_bytes)
        arq.write(tam.to_bytes(2, byteorder='big', signed=False))
        arq.write(registro_bytes)

        print(f'Registro inserido com sucesso: {registro}\nLocal: final do arquivo.')

        try:
            id_reg = int(campos[0])
            hashmap_ids[id_reg] = offset
        except ValueError:
            print(f"ID inválido: {campos[0]}")
    arq.seek(pos_atual)  # retorna à posição original, se necessário

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
        with open(arquivo, 'r+b') as arq:
            cabecalho_bytes = arq.read(4)
            cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
            print(f'Cabeçalho: {cabecalho}')

            resultado = buscaId(arq, 113, hashmap_ids)
            print(resultado)

            #novo_registro = '66|500 Dias com Ela|Marc Webb|2009|Comédia, Drama, Romance|95|Joseph Gordon|'
            #insertReg(arq, novo_registro, hashmap_ids)

    except FileNotFoundError:
        print('Arquivo não encontrado!')

if __name__ == '__main__':
    main('filmes.dat')
