"""Trabalho de ORD
Alunos:
Jader Alves dos Santos - RA120286
Janaina Maria Cera da Silva - RA115832
Lucas Rodrigues Fedrigo - RA129060"""

def leia_reg(file):
    offset = file.tell()
    tam_reg = file.read(2)
    if len(tam_reg) < 2:
        return None, None
    # converte os bytes para inteiro
    tam = int.from_bytes(tam_reg, byteorder='big', signed=False)
    if tam > 0:
        # armazena no buffer o texto do tamanho dos bytes
        buffer = file.read(tam)
        # transforma numa string
        buffer = buffer.decode()
        return offset, buffer
    else:
        return offset, ''

def main(arquivo: str) -> str:
    try:
        with open(arquivo, 'r+b') as arq:
            offsets = []
            arq.seek(0)
            cabecalho_bytes = arq.read(4)
            cabecalho = int.from_bytes(cabecalho_bytes, byteorder='big', signed=True)
            #print(cabecalho)
            while True:  
                offset, registro = leia_reg(arq)
                if offset is None:
                    break
                offsets.append(offset)
                #print(f'Offset {offset} | Registro: {registro.strip()}')
            print(offsets)
    except:
        FileNotFoundError('Arquivo não encontrado!')

if __name__ == '__main__':
    main('filmes.dat')