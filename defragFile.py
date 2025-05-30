from readReg import readReg

def defragFile(arq):
    arq.seek(0)
    arq.write((-1).to_bytes(4, byteorder='big', signed=True))  # Reinicia o cabeçalho da LED

    read_ptr = arq.tell()
    write_ptr = arq.tell()
    sobra = 0

    while True:
        arq.seek(read_ptr)
        data = readReg(arq, readLed=True)
        if data is None:
            break
        registro, tamanho, offset = data

        if isinstance(registro, int):  # Registro inválido
            sobra += tamanho + 2  # 2 bytes para o tamanho
            read_ptr = offset + 2 + tamanho
            continue

        if sobra > 0:
            arq.seek(write_ptr)
            arq.write(tamanho.to_bytes(2, byteorder='big', signed=False))
            arq.write(registro.encode('utf-8'))
            write_ptr += 2 + tamanho
        else:
            write_ptr = offset + 2 + tamanho

        read_ptr = offset + 2 + tamanho

    arq.truncate(write_ptr)
