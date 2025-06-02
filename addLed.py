from typing import BinaryIO, Optional

def addLed(
    arq: BinaryIO,
    actOffset: int,
    size: int,
    offset: int,
    prevOffset: Optional[int] = None,
    prevSize: Optional[int] = None,
    nextOffset: Optional[int] = None
) -> bool:
    """Adds a new pointer to the LED at the specified offset.
    If the pointer already exists, it updates the size and pointer accordingly to the size.
    If the pointer does not exist, it creates a new pointer at the specified offset.
    If the pointer is larger than the size, it updates the pointer to the new size.
    """
    if actOffset == -1 and prevOffset is None:
        arq.seek(offset + 2)
        arq.write(b'*' + (-1).to_bytes(4, 'big', signed=True))
        arq.seek(0)
        arq.write(offset.to_bytes(4, 'big', signed=True))
        print(f'Local: offset = {offset} bytes ({hex(offset)}).\n')
        return True

    arq.seek(actOffset)
    pointerSize: int = int.from_bytes(arq.read(2), 'big', signed=False)
    arq.read(1)
    nextOffset = int.from_bytes(arq.read(4), 'big', signed=True)

    if pointerSize > size:
        arq.seek(offset)
        arq.write(size.to_bytes(2, 'big', signed=False))
        arq.write(b'*' + actOffset.to_bytes(4, 'big', signed=True))
        print(f'Local: offset = {offset} bytes ({hex(offset)}).\n')
        if prevOffset is None:
            arq.seek(0)
            arq.write(offset.to_bytes(4, 'big', signed=True))
            return True
        else:
            arq.seek(prevOffset)
            arq.write(prevSize.to_bytes(2, 'big', signed=False))
            arq.write(b'*' + offset.to_bytes(4, 'big', signed=True))
            return True

    if size > pointerSize and nextOffset == -1:
        arq.seek(actOffset)
        arq.write(pointerSize.to_bytes(2, 'big', signed=False))
        arq.write(b'*' + offset.to_bytes(4, 'big', signed=True))
        arq.seek(offset)
        arq.write(size.to_bytes(2, 'big', signed=False))
        arq.write(b'*' + (-1).to_bytes(4, 'big', signed=True))
        print(f'Local: offset = {offset} bytes ({hex(offset)}).\n')
        return True

    return addLed(arq, nextOffset, size, offset, actOffset, pointerSize, nextOffset)
