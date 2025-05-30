from readReg import readReg
from addLed import addLed

def removeRegister(arq, id):
    """
    Marks a register as removed by writing a '*' at the beginning of the register.
    The function also updates the LED pointer to point to the next removed register.
    """
    print(f'Remoção do registro de chave "{id}"')
    arq.seek(0)
    ledHeader = int.from_bytes(arq.read(4), 'big', signed=True)
    data = readReg(arq)
    notRemoved = True
    while notRemoved == True and data is not None:
        register, size, offset = data
        if register.startswith('*'):
            # Already marked as removed
            data = readReg(arq)
            continue
        
        if int(register.split('|')[0]) == id:
            notRemoved = False
            if addLed(arq, ledHeader, size, offset) == True:
                return True
            break
        
        data = readReg(arq)
        if data is None:
            break
    if notRemoved:
        print("Erro: registro não encontrado.\n")