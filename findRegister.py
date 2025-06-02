from typing import BinaryIO, Optional, Tuple, Union
from readReg import readReg

def findRegister(arq: BinaryIO, id: int) -> Union[Tuple[str, int, int], bool]:
    """Searches for a register by its ID in the file."""
    print(f'Busca pelo registro de chave "{id}"')
    arq.seek(0)
    arq.read(4)

    data: Optional[Union[Tuple[str, int, int], Tuple[int, int, int]]] = readReg(arq)

    while data is not None:
        register, size, offset = data

        # Se o registro está removido, ignora
        if isinstance(register, str) and register.startswith('*'):
            data = readReg(arq)
            continue

        # Verifica se é o registro procurado
        if isinstance(register, str) and int(register.split('|')[0]) == id:
            print(f"{register} ({size} bytes)\nLocal: offset = {offset} ({hex(offset)})\n")
            return register, size, offset

        data = readReg(arq)

    print("Erro: registro não encontrado.\n")
    return False
