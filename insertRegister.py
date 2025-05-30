from readReg import readReg
from removeLed import removeLed

def insertRegister(arq, buffer):
    """
    Marks a register as removed by writing a '*' at the beginning of the register.
    The function also updates the LED pointer to point to the next removed register.
    """
    arq.seek(0)
    ledHeader = int.from_bytes(arq.read(4), 'big', signed=True)
    buffer_bytes = buffer.encode('utf-8')
    print(f'Inserção do registro de chave "{buffer.split('|')[0]}" ({len(buffer_bytes)} bytes)')
    
    if removeLed(arq, buffer_bytes, ledHeader, len(buffer_bytes)):
        return True