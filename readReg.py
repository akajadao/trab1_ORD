def readReg(arq, readLed=False):
    """
    Reads a record from the file and returns, according to the parameters:
    - the buffer content
    - the size (in bytes)
    - the offset in the file
    If the record is marked as removed (starts with '*'), returns the LED pointer.
    """
    offset = arq.tell()
    sizeBytes = arq.read(2)
    if len(sizeBytes) < 2:
        return None
    
    size = int.from_bytes(sizeBytes, 'big', signed=False)

    if size == 0:
        return None  # registro vazio ou inválido
    buffer = arq.read(size)
    
    if buffer.startswith(b'*'):
        if readLed:
            # Se o registro está marcado como removido e queremos ler o LED, retornamos o ponteiro LED
            ledPointer = int.from_bytes(buffer[1:5], 'big', signed=True)
            return ledPointer, size, offset
        # Registro marcado como removido, retorna o ponteiro LED
        buffer = buffer.decode(errors='ignore')
        return buffer, size, offset
    
    if len(buffer) < size:
        return None  # erro de leitura
    else:
        data = buffer.decode(errors='ignore')
        return data, size, offset
    return None