from typing import BinaryIO, Optional
from removeLed import removeLed

def insertRegister(arq: BinaryIO, buffer: str) -> Optional[bool]:
    """
    Inserts a register into the file. Attempts to reuse space via the LED (removed list).
    Converts the buffer to bytes and uses removeLed to write it in the appropriate location.
    """
    arq.seek(0)
    ledHeader: int = int.from_bytes(arq.read(4), 'big', signed=True)
    buffer_bytes: bytes = buffer.encode('utf-8')

    print(f'Inserção do registro de chave "{buffer.split("|")[0]}" ({len(buffer_bytes)} bytes)')

    if removeLed(arq, buffer_bytes, ledHeader, len(buffer_bytes)):
        return True

    return None
