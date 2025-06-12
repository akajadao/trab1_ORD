from typing import BinaryIO, Optional

def removeLed(
    arq: BinaryIO,
    buffer: bytes,
    actOffset: int,
    size: int,
    prevOffset: Optional[int] = None,
    prevSize: Optional[int] = None,
    nextOffset: Optional[int] = None
) -> bool:
    """Removes a pointer from the LED file at the specified offset."""
    
    if actOffset == -1 and prevOffset is None:
        arq.seek(0, 2)
        arq.write(size.to_bytes(2, 'big', signed=False))
        arq.write(buffer)
        print('Local: fim do arquivo.\n')
        return True

    arq.seek(actOffset)
    pointerSize: int = int.from_bytes(arq.read(2), 'big', signed=False)
    arq.read(1)
    nextOffset = int.from_bytes(arq.read(4), 'big', signed=True)

    if pointerSize >= size:
        arq.seek(actOffset)
        arq.write(pointerSize.to_bytes(2, 'big', signed=False))
        arq.write(buffer.ljust(pointerSize, b'\0'))
        print(f"Local: offset = {actOffset} bytes ({hex(actOffset)}).\n")

        if prevOffset is None and nextOffset == -1:
            arq.seek(0)
            arq.write((-1).to_bytes(4, 'big', signed=True))
            return True

        if prevOffset is None and nextOffset != -1:
            arq.seek(0)
            arq.write(nextOffset.to_bytes(4, 'big', signed=False))
            return True

        if prevOffset is not None:
            arq.seek(prevOffset)
            arq.write(prevSize.to_bytes(2, 'big', signed=False))
            arq.write(b'*' + nextOffset.to_bytes(4, 'big', signed=True))
            return True

    if size > pointerSize and nextOffset == -1:
        arq.seek(0, 2)
        arq.write(size.to_bytes(2, 'big', signed=False))
        arq.write(buffer)
        print('Local: fim do arquivo.\n')
        return True

    return removeLed(arq, buffer, nextOffset, size, actOffset, pointerSize, nextOffset)
