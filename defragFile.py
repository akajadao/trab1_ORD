from typing import BinaryIO, Optional, Tuple, Union
from readReg import readReg

def defragFile(arq: BinaryIO) -> None:
    """
    Defragmentation implementation for the LED file.
    This function resets the LED header, reads all valid (non-removed) records,
    and rewrites them contiguously in the file, removing gaps from deletions.
    """
    arq.seek(0)
    arq.write((-1).to_bytes(4, byteorder='big', signed=True))  # Reinicia o cabeçalho da LED

    read_ptr: int = arq.tell()
    write_ptr: int = arq.tell()
    rest: int = 0

    while True:
        arq.seek(read_ptr)
        data: Optional[Union[Tuple[str, int, int], Tuple[int, int, int]]] = readReg(arq, readLed=True)

        if data is None:
            break

        register, size, offset = data

        if isinstance(register, int):  # Registro removido (LED pointer)
            rest += size + 2  # 2 bytes do tamanho do registro
            read_ptr = offset + 2 + size
            continue

        # Se há espaço livre antes, movemos o registro para o write_ptr
        if rest > 0:
            arq.seek(write_ptr)
            arq.write(size.to_bytes(2, byteorder='big', signed=False))
            arq.write(register.encode('utf-8'))
            write_ptr += 2 + size
        else:
            # Nenhum espaço removido anteriormente, só avançamos o ponteiro de escrita
            write_ptr = offset + 2 + size

        read_ptr = offset + 2 + size
