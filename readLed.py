from readReg import readReg

def readLed(arq, header):
    """This function just print the LED to user."""
    try:
        if header == -1:
            print("LED -> fim")
            print("Total: 0 espaços disponíveis")
            print("A LED foi impressa com sucesso!")
            return
        total = 0
        output = "LED"
        while header != -1:
            arq.seek(header)
            data = readReg(arq, readLed=True)
            buffer, size, offset = data
            if buffer == None:
                break
            try:
                prox = int(buffer)
            except Exception as e:
                print(e)
                break
            output += f" -> [offset: {header}, tam: {size}]"
            total += 1
            header = prox
        
        output += " -> fim"
        print(output)
        print(f"Total: {total} espaços disponíveis")
        print("A LED foi impressa com sucesso!")
    except Exception as e:
        print(f"Erro ao imprimir LED: {e}")