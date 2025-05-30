def readReg(arq, readLed=False):
    """
    Lê um registro do arquivo e retorna, conforme os parâmetros:
    - o buffer do conteúdo
    - o sizeanho (em bytes)
    - o offset no arquivo
    Se o registro estiver marcado como removido (começa com '*'), retorna o ponteiro LED.
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