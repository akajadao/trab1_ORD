from typing import BinaryIO, Optional, Tuple, Union

def readReg(arq: BinaryIO, readLed: bool = False) -> Optional[Union[Tuple[int, int, int], Tuple[str, int, int]]]:
    """
    Reads a record from the file and returns, according to the parameters:
    - the buffer content or LED pointer (int if reading LED)
    - the size (in bytes)
    - the offset in the file

    If the record is marked as removed (starts with '*'), returns the LED pointer if readLed is True.
    """
    offset: int = arq.tell()
    sizeBytes: bytes = arq.read(2)

    if len(sizeBytes) < 2:
        return None

    size: int = int.from_bytes(sizeBytes, 'big', signed=False)

    if size == 0:
        return None  # registro vazio ou inválido

    buffer: bytes = arq.read(size)

    if buffer.startswith(b'*'):
        if readLed:
            # Retorna o ponteiro LED como int
            ledPointer: int = int.from_bytes(buffer[1:5], 'big', signed=True)
            return ledPointer, size, offset

        # Registro marcado como removido, mas readLed=False; retorna como string
        return buffer.decode(errors='ignore'), size, offset

    if len(buffer) < size:
        return None  # erro de leitura
    else:
        data: str = buffer.decode(errors='ignore')
        return data, size, offset
