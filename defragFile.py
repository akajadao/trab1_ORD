from readReg import readReg

def defragFile(arq):
    """Defragmentation implementation for the LED file.
    This function will read reset the header of the LED file, then read all valid registers,
    and write them back to the file, removing any gaps left by deleted registers.
    """
    arq.seek(0)
    arq.write((-1).to_bytes(4, byteorder='big', signed=True))  # Reinicia o cabeçalho da LED

    read_ptr = arq.tell()
    write_ptr = arq.tell()
    rest = 0

    while True:
        arq.seek(read_ptr)
        data = readReg(arq, readLed=True)
        if data is None:
            break
        register, size, offset = data

        if isinstance(register, int):  # register inválido
            rest += size + 2  # 2 bytes para o size
            read_ptr = offset + 2 + size
            continue

        if rest > 0:
            arq.seek(write_ptr)
            arq.write(size.to_bytes(2, byteorder='big', signed=False))
            arq.write(register.encode('utf-8'))
            write_ptr += 2 + size
        else:
            write_ptr = offset + 2 + size

        read_ptr = offset + 2 + size

    arq.truncate(write_ptr)
