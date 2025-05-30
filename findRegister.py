from readReg import readReg

def findRegister(arq, id):
    """Searches for a register by its ID in the file."""
    print(f'Busca pelo registro de chave "{id}"')
    arq.seek(0)
    arq.read(4)
    data = readReg(arq)
    register, size, offset = data
    while register:
        if data == None:
            break
        register, size, offset = data
        if register.startswith('*'):
            data = readReg(arq)
            continue
            
        if int(register.split('|')[0]) == id:
            print(f"{register} ({size} bytes)\nLocal: offset = {offset} ({hex(offset)})\n")
            return register, size, offset
        data = readReg(arq)
    print("Erro: registro não encontrado.\n")
    return False