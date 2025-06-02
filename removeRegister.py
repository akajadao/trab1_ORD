from typing import BinaryIO, Optional, Tuple, Union
from readReg import readReg
from addLed import addLed

def removeRegister(arq: BinaryIO, id: int) -> Optional[bool]:
    """
    Marks a register as removed by writing a '*' at the beginning of the register.
    The function also updates the LED pointer to point to the next removed register.
    """
    print(f'Remoção do registro de chave "{id}"')
    arq.seek(0)
    ledHeader: int = int.from_bytes(arq.read(4), 'big', signed=True)
    data: Optional[Union[Tuple[str, int, int], Tuple[int, int, int]]] = readReg(arq)
    notRemoved: bool = True

    while notRemoved and data is not None:
        register, size, offset = data

        # Verifica se o registro já foi removido
        if isinstance(register, str) and register.startswith('*'):
            data = readReg(arq)
            continue

        if isinstance(register, str) and int(register.split('|')[0]) == id:
            notRemoved = False
            if addLed(arq, ledHeader, size, offset) is True:
                return True
            break

        data = readReg(arq)
        if data is None:
            break

    if notRemoved:
        print("Erro: registro não encontrado.\n")
